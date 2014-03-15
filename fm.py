#!/usr/bin/python
#coding:utf-8
import httplib
import json
import os
import sys
import subprocess
import time,datetime
import pyglet
import threading,thread
import urllib,urllib2
import getpass
from cookielib import CookieJar
from cStringIO import StringIO
from PIL import Image
from getch import getch


reload(sys)
sys.setdefaultencoding('utf-8')

prog_str = "%3d%% [%-2s]"

class DoubanFM():
	def __init__(self):
		self.player = pyglet.media.Player()


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

	def play(self, opener=None, channel=0):
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

				length =  int(int(song['length']) / 5)
				#print "like:",song['like']
				title = song['title']+".mp3"
				FNULL = open(os.devnull, 'w')
				player = subprocess.call(['wget', '-c', song['url'], '-O', title], stdout=FNULL, stderr=subprocess.STDOUT)
				time.sleep(1)
				filename=title
				source=pyglet.media.load(filename)
				player=pyglet.media.Player()
				player.queue(source)
				player.play()

				is_pause = 0
				starttime = datetime.datetime.now()
				passedTime = starttime-starttime
				pauseTime=0

				while 1:
					PP = raw_input()

					if PP == "p": #播放/暂停(P)
						is_pause = self.pause(player, is_pause)
					if PP == "l": #查看播放列表(L)
						pass
					if PP == "n": #下一首(N)
						pass
					if PP == "c": #单曲循环/取消单曲循环(C)
						pass
					if PP == "i": #标红心/取消红心(I)
						pass
					if PP == "d": #不再播放(D)
						pass
					if PP == "c": #现则兆赫(C)
						pass
					if PP == "h": #帮助(H)
						pass
					if PP == "e": #退出(E)
						pass

				#for i in range(length):
				#	time.sleep(5)
				#	DoubanFM.progress(i, length)

				subprocess.call(['rm', title], stdout=FNULL, stderr=subprocess.STDOUT)
				print "\n"

	def getPlayList(self, channel='0', opener=None):
		url = 'http://douban.fm/j/mine/playlist?type=n&channel=' + channel + '&from=mainsite'
		if opener == None:
			return json.loads(urllib.urlopen(url).read())
		else:
			return json.loads(opener.open(urllib2.Request(url)).read())


	def progress(self, i, length):
		i = i+1
		sys.stdout.write(chr(0x0d))
		sys.stdout.write(prog_str % (i * 100 / length, i*'='))
		sys.stdout.flush()

	def pause(self, player, is_pause):
		print '\r暂停/播放'
		if is_pause:
			player.play()
			return 0
		else:
			player.pause()
			return 1
		

if __name__ == '__main__':
	print "Welcome to the DoubanFM"
	#user = raw_input('请输入用户名：')
	#password = getpass.getpass('密码：')
	DoubanFM = DoubanFM()
	#opener = DoubanFM.login(user, password)
	#DoubanFM.play(opener)
	DoubanFM.play()