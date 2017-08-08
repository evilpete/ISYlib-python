#!/usr/bin/env python

from __future__ import print_function

__author__ = "Peter Shipley"


from ISY.IsyClass import Isy, log_time_offset
from ISY.IsyEventData import LOG_USERID, LOG_TYPES

import sys
import getopt
import time

opt_nosec = 0
opt_tab = 0
opt_debug = 0
opt_error = 0
opt_errorlog = 0
opt_names = 0
opt_addr = None

time_const=2208988800;


def main(isy):

    if opt_errorlog:
        log_err(isy)
    else:
        log_sys(isy)


def log_err(isy):

    header = [ "Time", "UID", "Log Type", "Error Message" ]

    if opt_tab:
        fmt = "{0}\t{1}\t{2}\t{3}"
    else:
        fmt = "{:<15} {:<24} {:<38} {!s}"

    if opt_nosec:
        time_fmt = "%b %d %H:%M"
    else:
        time_fmt = "%b %d %H:%M:%S"

    time_offset = log_time_offset()

   # llimit = 200

    #print("{0} {1} {2} {3}".format(*header))
    print(fmt.format(*header))
    for log_line in isy.log_iter(error = 1):
        col = str(log_line).split("\t")

        # print("log_line : ", len(col), " : ", "|".join(col))
        if ( len(col) < 4 ):
            print("BAD log_line : ", len(col), " : ", "|".join(col))
            continue

        newtime = int(col[0]) - time_const - time_offset
        ti = time.localtime(newtime)
        col[0] = time.strftime(time_fmt, ti)
        col[1] = int(col[1])
        if col[1] < len(LOG_USERID) : col[1] = LOG_USERID[col[1]]
        if col[2] in LOG_TYPES : col[2] = LOG_TYPES[col[2]]

        print(fmt.format( *col ))

        #if llimit == 0:
        #    break


def log_sys(isy):

    nodefmt="{:<12}"
    commfmt="{:<4}"

    header = [ "Node", "Control", "Action", "Time", "UID", "Log Type" ]

    if opt_names:
        nodefmt="{:<18}"
        commfmt="{:<10}"
        print("opt_names = ", opt_names)

    if opt_tab:
        fmt = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}"
    else:
        fmt = nodefmt + " " + commfmt + " {:<20} {:<15} {:<15} {:<15}"

    if opt_nosec:
        time_fmt = "%b %d %H:%M"
    else:
        time_fmt = "%b %d %H:%M:%S"

    # fmt = "{0} {1} {2} {3} {4} {5}"

    time_offset = log_time_offset()

   # llimit = 200

    # print("{0} {1} {2} {3} {4} {5}".format(*header))
    print(fmt.format(*header))
    for log_line in isy.log_iter(error = opt_errorlog):
        col = str(log_line).split("\t")

        if opt_names:
            gn = isy._node_get_name(col[0])
            # print("n / gn = ", col[0], " / ", gn)
            if gn[1] is not None:
                col[0] = gn[1]

        newtime = int(col[3]) - time_const - time_offset
        ti = time.localtime(newtime)
        col[3] = time.strftime(time_fmt, ti)
        col[4] = int(col[4])
        if col[4] < len(LOG_USERID) : col[4] = LOG_USERID[col[4]]
        if col[5] in LOG_TYPES : col[5] = LOG_TYPES[col[5]]

        print(fmt.format( *col ))

        #if llimit == 0:
        #    break
        #llimit = llimit - 1


def parseargs():
    global opt_names, opt_addr, opt_errorlog, opt_debug, opt_tab, opt_nosec
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "ahetnsd:",
            ['help', 'error', 'debug', 'addr', 'tab', 'nosec', 'names'])
    except getopt.error as e:
        usage(1, e)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-n', '--names'):
            opt_names = 1
        elif opt in ('-a', '--addr'):
            opt_addr = arg
        elif opt in ('-e', '--error'):
            opt_errorlog = 1
        elif opt in ('-d', '--debug'):
            opt_debug = arg
        elif opt in ('-t', '--tab'):
            opt_tab = 1
        elif opt in ('-s', '--nosec'):
            opt_nosec = 1


def usage(code, msg=''):
    print(__doc__ % globals(), file=sys.stderr)
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(code)

if __name__ == '__main__':
    parseargs()
    myisy = Isy( addr=opt_addr, debug=opt_debug )
    main(myisy)
    exit(0)

