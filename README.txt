Bloger Tool
===========

Command line tool to communicate with blogger.com and blogspot.com.

This project contains single (and simple enough) console command named 'blog'.
Typical usage scenario:
    init project
$ blog init path/to/blog/articles
$ cd path/to/blog/articles
    setup user
$ blog user --email <user@gmail.com> --blogid <id of blog at blogger.com>
    make and edit article file
$ touch article.md
    add post to local database
$ blog add article.md
    open in browser locally generated html file for article.md
$ blog open article.md
    set labels
$ blog label article.md --add "bloggertool, console, blogspot.com"
    publish post on blosgspot.com
$ blog publish article.md
    edit article.md making some changes
$ ...
    synchronize remote presentation with local md file
$ blog push article.md

For other available commands please see
$ blog --help

------------------------------
