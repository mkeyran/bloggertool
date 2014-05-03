# help/help.py
# Copyright (C) 2011-2012 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import sys

from operator import itemgetter

import argparse

from bloggertool.str_util import T, a
from bloggertool.help import TOPICS, add_topic


HELP = T("Help about topics")
DESCR = T("""
    Aliases: --help, -h
    For list of available topics see
    {prog} help commands
    {prog} help topics
    """)


def print_list(iterable):
    lst = [(i[0], i[1]) for i in iterable]
    lst = sorted(lst, key=itemgetter(0))
    max_name = max(len(i[0]) for i in lst)
    for name, val in lst:
        sys.stdout.write("%s %s\n" % (name.ljust(max_name), val))


def make_help(root_parser, subparsers, commands):
    formatter = argparse.RawDescriptionHelpFormatter

    help_parser = subparsers.add_parser('help',
                                        help=HELP,
                                        description=HELP,
                                        epilog=DESCR.format(
                                            prog=root_parser.prog),
                                        formatter_class=formatter)

    help_parser.add_argument('topic', nargs='?',
                             default=None,
                             help='Topic name')

    help_parser.add_argument('--usage',
                             action='store_true',
                             default=False,
                             help="display usage message and exit")

    commands = dict(commands)
    commands['help'] = help_parser
    commands[None] = root_parser

#    for topic_name, (help_message, topic_body) in TOPICS:
#        topics

    class Runner(object):
        require_load_config = False
        config = None

        def __init__(self, args):
            self.topic = args.topic
            self.usage = args.usage

        def run(self):
            if self.topic in commands:
                parser = commands[self.topic]
                if self.usage:
                    parser.print_usage()
                else:
                    parser.print_help()
                parser.exit()
            elif self.topic in TOPICS:
                topic = TOPICS[self.topic]
                sys.stdout.write(topic.title)
                sys.stdout.write('\n\n')
                sys.stdout.write(topic.text)
                sys.stdout.write('\n')
                root_parser.exit()
            elif self.topic == 'commands':
                sys.stdout.write("List of available commands:\n\n")
                print_list((name, val.description)
                           for name, val in commands.iteritems()
                           if name is not None)
                root_parser.exit()
            elif self.topic == 'topics':
                sys.stdout.write("List of available topics:\n\n")
                print_list((name, val.title)
                           for name, val in TOPICS.iteritems())
                root_parser.exit()
            else:
                sys.stdout.write(a("""
                    Unknown help topic: {self.topic}
                    Use {root_parser.prog} help for list of available topics
                    """) + '\n')
                root_parser.exit()

    help_parser.set_defaults(cmd=Runner)
