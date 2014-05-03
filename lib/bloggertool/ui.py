# ui.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import sys
from urllib2 import urlopen


def get_captcha(url):
    print "Please open in browser <%s> and enter captcha in next prompt" % url
    return raw_input('Captcha: ')


def ask(prompt, answers='y/N'):
    list_answers = answers.split('/')
    default = [i.lower() for i in list_answers if i.isupper()]
    assert len(default) < 2, 'Specifiy only one default!!! %s' % answers
    default = default[0] if default else None
    list_answers = [i.lower() for i in list_answers]
    print prompt  # XXX check for russian letters
    ret = raw_input('[%s]: ' % answers)
    while True:
        if not ret and default:
            ret = default
        if not ret in list_answers:
            ret = raw_input("Please specify one of [%s]: " % answers)
        else:
            return ret
