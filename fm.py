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

        global cycle, startplay
        playlist = None
        startplay = True
        cycle = False
        while startplay:
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
                if startplay == False:
                    break


class MusicPlayer():

    def __init__(self, song, channel, playlist):
        self.song = song
        self.channel = channel
        self.playlist = playlist

    def play(self):
        global pause_flag, ret, pasuetime, passedTime, song_length, starttime, song_like
        song = self.song
        channel = self.channel
        playlist = self.playlist
        fnull = open(os.devnull, "w")
        # 播放
        print '--------------------'
        print '当前频道:', constant.Channel.get(channel)
        print '歌曲:', song['title']
        print '演唱者:', song['artist']
        # print '评分：' + str(song['rating_avg'])
        song_like = song['like']
        if song_like == 1:
            if channel != -3:
                print '已标记喜欢'
        print '--------------------'

        player = subprocess.Popen(
            ['mplayer', '-af', 'volume=0', song['url']], stdin=subprocess.PIPE, stdout=fnull, stderr=fnull)

        ret = song['length']
        pause_flag = 0
        starttime = datetime.datetime.now()
        pasuetime = starttime - starttime
        song_length = song['length']

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
                ret = song_length - passedTime.seconds
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
            rd = select([sys.stdin], [], [], ret)[0]
            if not rd:
                return "None"
            else:
                x = raw_input()
                y = ''
                if x.isdigit():
                    y = str(x)
                    x = 'channel'
                else:
                    x = x.lower() 
                {
                    'o': lambda x: self.sing(self.song, self.channel),
                    'p': lambda x: self.pause(self.player, self.song),
                    'l': lambda x: self.showlist(self.playlist),
                    '+': lambda x: self.increaseV(self.player),
                    '-': lambda x: self.decreaseV(self.player),
                    'c': lambda x: self.cycle(),
                    'i': lambda x: self.love(self.channel, self.song),
                    'd': lambda x: self.delete(self.channel, self.song, self.player),
                    'h': lambda x: self.help(),
                    'e': lambda x: self.quit(self.player),
                    'n': lambda x: self.nextsong(self.player),
                    'channel': lambda x: self.changech(x, self.player),
                }[x](y)

    def nextsong(self, player):
        print '下一首'
        global song_length, ret
        player.stdin.write('q')
        ret = 0
        song_length = 0
        self.stop()

    def sing(self, song, channel):
        global song_like
        print '--------------------'
        print '当前频道:', constant.Channel.get(channel)
        print '歌曲:', song['title']
        print '演唱者:', song['artist']
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
            ret = song_length - passedTime.seconds - 0.1
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
            print num, '.', song['title'][0:24 - zh].ljust(24 - zh),
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
        if cycle == True:
            print '单曲播放\n'
            cycle = False
        else:
            print '顺序播放\n',
            cycle = True

    def love(self, channel, song):
        global song_like
        url = 'http://douban.fm/j/mine/playlist?type=b&sid=' + \
            song['sid'] + '&channel=' + str(channel) + '&from=mainsite'
        if song_like == 0:
            song_like = 1
            print '您设置了喜欢这首歌曲'
        else:
            song_like = 0
            print '你取消了喜欢这首歌曲'
        return json.loads(opener.open(urllib2.Request(url)).read())

    def delete(self, channel, song, player):
        global song_like
        url = 'http://douban.fm/j/mine/playlist?type=r&sid=' + \
            song['sid'] + '&channel=' + str(channel) + '&from=mainsite'
        print '您设置了不在收听这首歌曲'
        json.loads(opener.open(urllib2.Request(url)).read())
        time.sleep(0.1)
        self.nextsong(self.player)

    def changech(self, x, player):
        global opener, song_length, ret, startplay
        player.stdin.write('q')
        time.sleep(0.2)
        ret = 0
        song_length = 0
        self.stop()
        startplay = False
        time.sleep(0.4)
        DoubanFM.play(opener=opener, channel=int(x))

    def help(self):
        print chr(27) + "[2J"
        print 'This a Fm project, and the music data is come from Douban.\n\
    O: Currently playing music\n\
    P: Pause, Resume playback\n\
    L: Playlist\n\
    +: Increases the volume\n\
    -: Decrease the volume\n\
    C: Loop\n\
    N: Next song\n\
    I: Tag like music\n\
    D: No longer play\n\
    E: Exit\n\
    H: Help\n\
    \n\
    Change channel:\n\
    -3 :红心\n\
    0  :私人\n\
    1  :华语\n\
    2  :欧美\n\
    3  :七零\n\
    4  :八零\n\
    5  :九零\n\
    6  :粤语\n\
    7  :摇滚\n\
    8  :民谣\n\
    9  :轻音乐'

    def quit(self, player):
        print '退出',
        global song_length, ret, startplay
        player.stdin.write('q')
        time.sleep(0.5)
        ret = 0
        song_length = 0
        self.stop()
        startplay = False
        raise SystemExit

    def stop(self):
        self.thread_stop = True


if __name__ == '__main__':
    global opener
    print "Welcome to the DoubanFM"
    user = raw_input('请输入用户名')
    password = getpass.getpass('密码：')
    DoubanFM = DoubanFM()
    opener = DoubanFM.login(user, password)
    DoubanFM.play(opener=opener, channel = -3)
    # DoubanFM.play()
