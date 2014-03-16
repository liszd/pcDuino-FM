#!/usr/bin/python
#coding:utf-8
import httplib
import json
import os
import sys
import subprocess
import time,datetime
import urllib,urllib2
import getpass
from cookielib import CookieJar
from cStringIO import StringIO
from PIL import Image
import getch

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

	def getPlayList(self, channel='0', opener=None):
		url = 'http://douban.fm/j/mine/playlist?type=n&channel=' + channel + '&from=mainsite'
		if opener == None:
			return json.loads(urllib.urlopen(url).read())
		else:
			return json.loads(opener.open(urllib2.Request(url)).read())

	def play(self, opener=None, channel=0):

		global pauseTime ,pause_flag, starttime, volume
		fnull=open(os.devnull,"w")
		while True:
			if opener == None:
				playlist = DoubanFM.getPlayList("0")
			else:
				playlist = DoubanFM.getPlayList("-3", opener)
			if playlist['song'] == []:
				print '获取播放列表失败'
				break

			# 获取播放列表
			for song in playlist['song']:

				# 播放
				print '--------------------'
				if channel == '-3':
					print '当前频道：红心频道'
				else:
					print '当前频道：'+str(channel)+'号电台'
				print '歌曲：'+song['title']
				print '演唱者：'+song['artist']
				print '评分：'+str(song['rating_avg'])
				if song['like'] == 1:
					print '已标记喜欢'
				print '--------------------'

				player = subprocess.Popen(['mplayer', '-af', 'volume=0', song['url']], stdin=subprocess.PIPE,stdout=fnull,stderr=fnull)

				starttime = datetime.datetime.now()
				ret=0
				currenttime=datetime.datetime.now()
				passedTime=currenttime-starttime

				pauseTime=0
				pause_flag=0

				while((passedTime.seconds-pauseTime)<30):
					PP = getch.getch()

					if PP == "n": #下一首(N)
						time.sleep(0.5)
						break
					else:
						self.choose(PP, player, playlist, song)
						time.sleep(0.5)

				print "\n"
				try:
					player.stdin.write('q')
				except OSError:
					pass


	def choose(self, PP, player, playlist, song):
		return {
		'p':lambda x:self.pause(player, song),
		'l':lambda x:self.showlist(playlist),
		'+':lambda x:self.increaseV(player),
		'-':lambda x:self.decreaseV(player),
		#'c':self.cycle(PP),
		#'i':self.love(player),
		#'d':#不再播放(D) (Not finished),
		#'c':#现则兆赫(C) (Not finished),
		#'h':#帮助(H) (Not finished),
		#'e':#退出(E) (Not finished),
		'n':'',
		}.get(PP,'n')('n')

	def pause(self, player, song):
		global pause_flag, pauseTime, pauseStartTime, starttime
		player.stdin.write('p')
		time.sleep(0.2)
		if pause_flag==0:
			print '暂停'
			pauseStartTime=datetime.datetime.now()
			pause_flag=1
			currenttime=datetime.datetime.now()
			passedTime=currenttime-starttime
			lastTime = 30 - passedTime.seconds + pauseTime
			print '剩余时间:%.2d分%.2d秒\r' % ((song['length']-passedTime.seconds+pauseTime)/60,(song['length']-passedTime.seconds+pauseTime)%60),
		else:
			print '播放'
			pauseTime=pauseTime + (datetime.datetime.now()-pauseStartTime).seconds+1
			pause_flag=0

	def showlist(self, playlist):
		num = 0
		for song in playlist['song']:
			num = num+1
			print num,'.', song['title'].ljust(20),
			print "-:",song['artist']
			if num > 5:
				break

	def increaseV(self, player):
		print '增加音量',
		player.stdin.write('0')

	def decreaseV(self, player):
		print '减小音量',
		player.stdin.write('9')

	def cycle(self, player):
		print '单曲播放/顺序播放',
		c = 0 if cycle else 1

	def love(self, player):
		print '标红心/取消红心',
		
	def delete(self, player):
		time.sleep(0.5)


	def channel(self, PP):
		PP = ['','']
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
			print "-1  红心"
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

if __name__ == '__main__':
	print "Welcome to the DoubanFM"
	#user = raw_input('请输入用户名：')
	#password = getpass.getpass('密码：')
	DoubanFM = DoubanFM()
	#opener = DoubanFM.login(user, password)
	#DoubanFM.play(opener)
	DoubanFM.play()