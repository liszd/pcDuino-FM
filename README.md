pcDuino-FM
==========

###目标
这算是我FYP的一部分吧
FYP想做一个可以听歌，识别歌曲的盒子。
这一部分就只是豆瓣fm的功能。

另外自己还有个曲库，做进一步的听歌和识别。

###以下都是构想，就当立牌坊

####登入

暂时没有解决登入的验证码

1. orc文字识别？
2. 手机蓝牙登入？

####频道

```
-3   红心
 0   私人
 1   华语
 2   欧美
 3   七零
 4   八零
 5   九零
 6   粤语
 7   摇滚
 8   民谣
 9   轻音乐
10   电影原声
```

####功能

```
"p": #播放/暂停(P)
"l": #查看播放列表(L)
"n": #下一首(N)
"c": #单曲循环/取消单曲循环(C)
"i": #标红心/取消红心(I)
"d": #不再播放(D)
"c": #现则兆赫(C)
"h": #帮助(H)
"e": #退出(E)
```

####进度


1. 登入 - 在terminal中输入账号密码，弹窗显示验证码输入
2. 播放 - 显示进度条，暂停等

准备换MP3-library, 现在用的 `pyhlet` 只能播放本地歌曲，下一步换成`pygst`。

###废话说我完
```
代码还没有写完。。。
```