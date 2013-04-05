#!/usr/local/bin/python2.7

from ISY.IsyClass import Isy, log_time_offset
from ISY.IsyEventData import LOG_USERID, LOG_TYPES

import sys
import getopt
import time

opt_debug = 0
opt_error = 0
opt_errorlog = 0
opt_nonames = 1

time_const=2208988800;


def main():

    parseargs()

    myisy = Isy( debug=opt_debug )

    nodefmt="%-18s";
    commfmt="%-10s";

    header = [ "Node", "Control", "Action", "Time", "UID", "Log Type" ]

    if opt_nonames :
	nodefmt="{:<12}"
	commfmt="{:<4}"

    fmt = nodefmt + " " + commfmt + " {:<20} {:<15} {:<15} {:<15}"
    # fmt = "{0} {1} {2} {3} {4} {5}"

    time_offset = log_time_offset()

    llimit = 200

    # print "{0} {1} {2} {3} {4} {5}".format(*header)
    print fmt.format(*header)
    for log_line in myisy.log_iter(error = opt_errorlog) :
	col = str(log_line).split("\t")

	newtime = int(col[3]) - time_const - time_offset
	ti = time.localtime(newtime)
	col[3] = time.strftime("%b %d %H:%M:%S", ti)
	if col[4] < len(LOG_USERID) : col[4] = LOG_USERID[col[4]]
	if col[5] in LOG_TYPES : col[5] = LOG_TYPES[col[5]]

	print fmt.format( *col )

	if llimit == 0 :
	    break
	llimit = llimit - 1


def parseargs():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hed:",
            ['help', 'error', 'debug'])
    except getopt.error, e:
        usage(1, e)
 
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-n', '--nonames'):
            opt_nonames = 1
        elif opt in ('-e', '--error'):
            opt_errorlog = 1
        elif opt in ('-d', '--debug'):
            opt_debug = arg 


def usage(code, msg=''):
    print >> sys.stderr, __doc__ % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

if __name__ == '__main__' :
    main()
    exit(0)

