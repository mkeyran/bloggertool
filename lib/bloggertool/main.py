# main.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
import os
import sys

import argparse

from bloggertool.__version__ import __version__
from bloggertool.commands import commands
from bloggertool.encoding import setup_encoding
from bloggertool.help import make_help
from bloggertool.log_util import setup_log
from bloggertool.str_util import T

log = logging.getLogger(__name__)

DESCRIPTION = T("blogspot.com tool")
EPILOG = T("""
    For more information use
    {prog} help commands
    {prog} help topics
    """)


class UsageAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(UsageAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_usage()
        parser.exit()


def istty():
    """return True if interactive mode aka tty device"""
    stdout = sys.stdout
    # some file-like objects used to forget to define that method
    isatty = getattr(stdout, 'isatty', None)
    if isatty is not None:
        return isatty()
    else:
        return False


def main():
    prog = os.path.basename(sys.argv[0])

    formatter = argparse.RawDescriptionHelpFormatter
    #formatter = argparse.ArgumentDefaultsHelpFormatter
    shared = argparse.ArgumentParser("Shared options",
                                     add_help=False,
                                     formatter_class=formatter)
    shared.add_argument('-V', '--verbose',
                        action='store_true', default=False,
                        help="verbose output")
    shared.add_argument('--show-traceback',
                        action='store_true', default=False,
                        help="display exception traceback if occured")
    shared.add_argument('--usage',
                        action=UsageAction,
                        help="display usage message and exit")
    shared.add_argument('--console-encoding',
                        default=None,
                        help="Preferred encoding for console."
                        "See topic 'encodings' for more information")

    #### Ugly argparse version workaround
    old_parser = argparse.__version__.split('.') < (1, 1)
    kwargs = {'version': __version__} if old_parser else {}
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     parents=[shared],
                                     epilog=EPILOG(prog=prog),
                                     prog=prog,
                                     formatter_class=formatter,
                                     **kwargs)
    if not old_parser:
        parser.add_argument('-v', '--version',
                            action='version',
                            version=__version__)
    #### end workaround

    subparsers = parser.add_subparsers()

    command_parsers = {}

    for cmd in sorted(commands, key=lambda cmd: cmd.NAME):
        assert cmd.NAME, 'NAME is missing in %s' % cmd.__name__
        assert cmd.DESCR, 'DESCR is missing in %s' % cmd.__name__
        assert cmd.HELP, 'HELP is missing in %s' % cmd.__name__
        sub_parser = subparsers.add_parser(cmd.NAME, help=cmd.HELP,
                                           description=cmd.HELP,
                                           epilog=cmd.DESCR,
                                           parents=[shared],
                                           formatter_class=formatter)
        cmd.fill_parser(sub_parser)
        sub_parser.set_defaults(cmd=cmd)

        if cmd.require_interactive:
            sub_parser.add_argument('-i', '--interactive',
                                dest='interactive',
                                action='store_const',
                                const=None,
                                help=("prompt before overwrite."
                                      "Default for tty devices"))
            sub_parser.add_argument('-f', '--force',
                                dest='interactive',
                                action='store_true',
                                help=("do not prompt before overwriting"))
            sub_parser.add_argument('-n', '--no-clobber',
                                dest='interactive',
                                action='store_false',
                                help=("do not any overwrite."
                                      "Default for non-tty devices"))
            sub_parser.set_defaults(interactive=None if istty() else False)

        command_parsers[cmd.NAME] = sub_parser

    make_help(parser, subparsers, command_parsers)

    args = parser.parse_args()

    setup_encoding(args.console_encoding)
    setup_log(args)

    try:
        cmd = args.cmd(args)
        if cmd.require_load_config:
            cmd.load_config(args)
        ret = cmd.run()
        if cmd.config is not None and cmd.config.need_save:
            cmd.config.save()
        return ret
    except Exception, ex:
        if args.show_traceback:
            log.exception("Exception occured: %s", ex)
        else:
            log.error("%s", ex)
        return 255
    except KeyboardInterrupt:
        if args.show_traceback:
            log.exception("Exit by user interrupt")
        else:
            log.warning("Exit by user interrupt")
        return 254
