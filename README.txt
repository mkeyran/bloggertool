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
$ touch article.rst 
    add post to local database
$ blog add article.rst
    open in browser locally generated html file for article.rst
$ blog open article.rst 
    set labels
$ blog label article.rst --add "bloggertool, console, blogspot.com"
    publish post on blosgspot.com
$ blog publish article.rst
    edit article.rst making some changes
$ ...
    synchronize remote presentation with local rst file
$ blog push article.rst 

For other available commands please see
$ blog --help

------------------------------
