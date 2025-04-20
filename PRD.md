# 概述
1. 写一个py脚本爬虫，beautifulsoup获取小红书链接里的标题名称、视频文件、图片、文字
写一个py脚本爬虫，爬取这个网站@https://lexfridman.com/robert-rodriguez-transcript 的内容，保存标题（class="entry-title"），Transcript文本内容（ts-segment），原视频链接，封面
2. 将这脚本通过fastapi做成api，input是一个链接，输出标题名称、视频文件、图片、文字。
3. 能够通过快捷指令，将小红书内容保存到手机备忘录