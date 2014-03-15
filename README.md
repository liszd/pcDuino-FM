pcDuino-FM
==========

This is a Part of my FYP(Final Year Project)  
My FYP will build a Music Box.  
The pcDuino-FM will be one of the main funcion.  
Other function include music listening, music identify.  

And now it still run on python.

##Update
---

###Version.2
Change the media library from `pyglet` to `mplayer`  
Add new function about library volume

###Version.1
Fundamentally finish the main function  
1. Can login in with Douban account.  
2. Can listen music. (If login, will listen `红心` music, else listen `私人` music)  
3. Use `pyget` play music.(It can't listen url, need to download. Maybe I will change the libary, like `pyglet`)  
4. music progress bar  
5. music can be pasued  

##Features
---
It also not finish yet.

##Installation
---
```
pip install getpass
brew install PIL
pip install getch
brew install mplayer
```

##How to use
---
###Login

login Douban. Input the account, password, and verification code.
verification code will be showed as picture.
And I know it is not a good way to show verification code, maybe I will try buletooth in future

###Function
Choose the  function  

```
"p"：# Play/Pause(P)
"l"：# Get the playlist(L)
"n"：# Next music(N)
"+"：# Increase volume(+) (have bug)
"-"：# Decrease Volume(-) (have bug)
"c"：#单曲循环/取消单曲循环(C)(Not finished)
"i"：#标红心/取消红心(I) (Not finished)
"d"：#不再播放(D) (Not finished)
"c"：#现则兆赫(C) (Not finished)
"h"：#帮助(H) (Not finished)
"e"：#退出(E) (Not finished)
```
###Channel
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

## License
---
(The MIT License)

Copyright (c) 2014 Liam <lidzd1992@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
