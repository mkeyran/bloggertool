#!/usr/bin/env python

import traceback
import sys

from regression import scenario

try:
    scenario.run()
except Exception, ex:
    print "Error in scenario"
    tb = tb2 = sys.exc_info()[2]
    tb_len = 1
    while tb2.tb_next:
        tb_len += 1
        tb2 = tb2.tb_next
    traceback.print_tb(tb, tb_len - 1, sys.stdout)
    print ex
