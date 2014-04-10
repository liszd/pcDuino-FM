#!/usr/bin/python
# coding:utf-8
import httplib
import json
import os
import sys
import subprocess
import time
import datetime
import threading
import urllib
import urllib2
import getpass
from cookielib import CookieJar
from cStringIO import StringIO
from PIL import Image
import getch
import re
from select import select
import constant

reload(sys)
sys.setdefaultencoding('utf-8')

prog_str = "%3d%% [%-2s]"


class DoubanFM():

	def login(self, username, password):
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
		while True:
			captcha_id = opener.open(urllib2.Request(
				'http://douban.fm/j/new_captcha')).read().strip('"')
			url = 'http://douban.fm/misc/captcha?size=m&id=' + captcha_id
			file = urllib2.urlopen(url)
			tmpIm = StringIO(file.read())
			im = Image.open(tmpIm)
			im.show()
			captcha = raw_input('验证码: ')
			print '登录中……'
			response = json.loads(opener.open(
				urllib2.Request('http://douban.fm/j/login'),
				urllib.urlencode({
								 'source': 'radio',
								 'alias': username,
								 'form_password': password,
								 'captcha_solution': captcha,
								 'captcha_id': captcha_id,
								 'task': 'sync_channel_list'})).read())
			if 'err_msg' in response.keys():
				print response['err_msg']
				if not response['err_msg'].startswith("验证码"):
					user = raw_input('请输入用户名：')
					password = getpass.getpass('密码：')
			else:
				print '登录成功'
				return opener

	def getPlayList(self, channel=0, opener=None):
		channel = str(channel)
		url = 'http://douban.fm/j/mine/playlist?type=n&channel=' + \
			channel + '&from=mainsite'
		if opener == None:
			return json.loads(urllib.urlopen(url).read())
		else:
			return json.loads(opener.open(urllib2.Request(url)).read())

	def play(self, opener=None, channel=0):
		
		global cycle
		cycle = False
		while True:
			if opener == None:
				playlist = DoubanFM.getPlayList(channel)
			else:
				playlist = DoubanFM.getPlayList(channel, opener)
			if playlist['song'] == []:
				print '获取播放列表失败'
				break

			# 获取播放列表
			for song in playlist['song']:
				player = MusicPlayer(song, channel, playlist)
				player.play()
				while cycle:
					player.play()


class MusicPlayer():
	def __init__(self, song, channel, playlist):
		self.song = song
		self.channel = channel
		self.playlist  =playlist

	def play(self):
		global pause_flag, ret, pasuetime, passedTime, song_length, starttime, song_like
		song = self.song
		channel = self.channel
		playlist = self.playlist
		fnull = open(os.devnull, "w")
		# 播放
		print '--------------------'
		print '当前频道:', constant.Channel.get(channel)
		print '歌曲:' , song['title']
		print '演唱者:' , song['artist']
		# print '评分：' + str(song['rating_avg'])
		song_like = song['like']
		if song_like == 1:
			if  channel != -3:
				print '已标记喜欢'
		print '--------------------'

		player = subprocess.Popen(
			['mplayer', '-af', 'volume=0', song['url']], stdin=subprocess.PIPE, stdout=fnull, stderr=fnull)

		ret = song['length']
		pause_flag = 0
		starttime = datetime.datetime.now()
		pasuetime = starttime - starttime
		song_length  = song['length']

		playerthread = PlayerControl(player, playlist, song, channel)
		processthread = ProcessControl(playerthread)

		processthread.start()
		playerthread.start()
		processthread.join()

		try:
			playerthread.exit()
			player.stdin.write('q')
		except Exception, e:
			pass
		else:
			pass

class ProcessControl(threading.Thread):
	def __init__(self, playerthread):
		threading.Thread.__init__(self)
		self.playerthread = playerthread

	def run(self):
		playerthread = self.playerthread
		lock = threading.Lock()
		global ret, pasuetime, passedTime, song_length, starttime
		while(ret > 0):
			with lock:
				currenttime = datetime.datetime.now()
				passedTime = currenttime - starttime - pasuetime
				ret = song_length- passedTime.seconds
				# print ret
				if ret < 3:
					playerthread.stop()

class PlayerControl(threading.Thread):

	def __init__(self, player, playlist, song, channel):
		threading.Thread.__init__(self)
		self.player = player
		self.playlist = playlist
		self.song = song
		self.channel = channel
		self.thread_stop = False

	def run(self):
		while not self.thread_stop:
			time.sleep(0.2)
			global pause_flag, ret
			if pause_flag == 0:
				ret = 999999
			rd = select([sys.stdin],[],[],ret)[0]
			if not rd:
				return "None"
			else:
				{
					'o': lambda x: self.sing(self.song, self.channel),
					'p': lambda x: self.pause(self.player, self.song),
					'l': lambda x: self.showlist(self.playlist),
					'+': lambda x: self.increaseV(self.player),
					'-': lambda x: self.decreaseV(self.player),
					'c': lambda x: self.cycle(),
					'i': lambda x: self.love(self.channel, self.song),
					# 'd':#不再播放(D) (Not finished),
					# 'c':#现则兆赫(C) (Not finished),
					# 'h':#帮助(H) (Not finished),
					# 'e':#退出(E) (Not finished),
					'n': lambda x: self.nextsong(self.player),
				}[raw_input().lower()]('')
	
	def nextsong(self, player):
		global song_length, ret
		player.stdin.write('q')
		ret = 0
		song_length = 0
		self.stop()
	
	def sing(self, song, channel):
		global song_like
		print '--------------------'
		print '当前频道:', constant.Channel.get(channel)
		print '歌曲:' , song['title']
		print '演唱者:' , song['artist']
		# print '评分：' + str(song['rating_avg'])
		if song_like == 1:
			print '已标记喜欢'
		print '--------------------'
	
	def pause(self, player, song):
		global pause_flag, ret, pasuetime, beginpause, song_length, passedTime
		player.stdin.write('p')
		if pause_flag == 0:
			print '暂停'
			beginpause = datetime.datetime.now()
			pause_flag = 1
			ret = song_length- passedTime.seconds-0.1
			print '剩余时间:%.2d分%.2d秒\r' % (ret / 60, ret % 60)
		else:
			print '播放'
			endpause = datetime.datetime.now()
			pause_flag = 0
			pasuetime = pasuetime + endpause - beginpause
			
	def len_zh(self, data):
		temp = re.findall('[^\x00-\xff]+', data)
		count = 0
		for i in temp:
			count += len(i)
		return(count)

	def showlist(self, playlist):
		num = 0
		for song in playlist['song']:
			num = num + 1
			zh = self.len_zh(song['title'][0:24])
			print num, '.', song['title'][0:24-zh].ljust(24-zh),
			print "-:", song['artist']
			if num > 5:
				break

	def increaseV(self, player):
		print '增加音量\n',
		player.stdin.write('0')

	def decreaseV(self, player):
		print '减小音量\n',
		player.stdin.write('9')

	def cycle(self):
		global cycle
		print '单曲播放/顺序播放\n',
		cycle = False if cycle == True else True

	def love(self, channel, song):
		global song_like
		# print '标红心/取消红心\n',
		url = 'http://douban.fm/j/mine/playlist?type=r&sid=' + song['sid'] + '&channel=' + str(channel) + '&from=mainsite'
		if song_like==0:
			song_like = 1
			print '您设置了喜欢这首歌曲'
		else:
			song_like = 0
			print '你取消了喜欢这首歌曲'
		return json.loads(opener.open(urllib2.Request(url)).read())

	def delete(self, player):
		time.sleep(0.5)

	def channel(self, PP):
		PP = ['', '']
		PP = PP.split(" ")
		if PP[1] == -1:
			pass
		elif PP[1] == 0:
			pass
		elif PP[1] == 1:
			pass
		elif PP[1] == 2:
			pass
		elif PP[1] == 3:
			pass
		elif PP[1] == 4:
			pass
		elif PP[1] == 5:
			pass
		elif PP[1] == 6:
			pass
		elif PP[1] == 7:
			pass
		elif PP[1] == 8:
			pass
		elif PP[1] == 9:
			pass
		elif PP[1] == 10:
			pass
		else:
			print '选择兆赫：(c 数字)'
			print "-3  红心"
			print "0   私人"
			print "1   华语"
			print "2   欧美"
			print "3   七零"
			print "4   八零"
			print "5   九零"
			print "6   粤语"
			print "7   摇滚"
			print "8   民谣"
			print "9   轻音乐"
			print "10  电影原声"

	def help(self, player):
		print '暂停/播放r',
		player.stdin.write('p')

	def quit(self, player):
		print '暂停/播放r',
		player.stdin.write('q')

	def stop(self):
		self.thread_stop = True


if __name__ == '__main__':
	print "Welcome to the DoubanFM"
	user = raw_input('请输入用户名：')
	password = getpass.getpass('密码：')
	DoubanFM = DoubanFM()
	opener = DoubanFM.login(user, password)
	DoubanFM.play(opener=opener, channel = -3)
	# DoubanFM.play()
