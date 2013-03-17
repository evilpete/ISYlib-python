#!/usr/local/bin/python2.7

import ISY

import sys
import getopt

class Options:
    debug = 0
    error = 0

def usage(code, msg=''):
    print >> sys.stderr, __doc__ % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def parseargs():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hed:",
            ['help', 'error', 'debug'])
    except getopt.error, e:
        usage(1, e)
 
    options = Options()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-e', '--error'):
            options.list = 1
        elif opt in ('-d', '--debug'):
            options.debug = arg 

    return options

def print_log(myisy, err) :
    for li in myisy.log_iter(error = err) :
       print li

if __name__ == '__main__' :

    options = parseargs()
    myisy = ISY.Isy( debug=options.debug )
    print_log(myisy, err=options.error)

