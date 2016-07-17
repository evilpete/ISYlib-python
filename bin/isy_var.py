#!/usr/bin/env python

"""list ISY vars demo app

Usage: %(program)s [options] [var=val]

Options:

    --list

"""
#this is Ugly code and should be cleaned up

__author__ = "Peter Shipley"

import ISY
import sys

import getopt


def list_vars_bash(myisy, csh=0):

    if csh:
        fmt = "set {0}={1}"
    else:
        fmt = "{0}={1}"

    for var in myisy.var_iter():
        print fmt.format( var.name, var.value )

def list_vars(myisy):
    fmt = "{:<4} : {:<19}{:<5}\t{:<5}\t{:}"
    print fmt.format( "ID", "NAME", "VAL", "INIT", "DATE" )
    for var in myisy.var_iter():
        print fmt.format( var.id, var.name, var.value, var.init, var.ts )

def usage(code, msg=''):
    print >> sys.stderr, __doc__
    print "globals ", globals()
    # % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

class Options:
    debug = 0
    olist = 0   # olist cause "list" was taken
    bash = 0
    csh = 0

def parseargs():
    options = Options()

    # shortcut
    if len(sys.argv) == 1:
        options.olist = 1
        return options, []

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hbldc",
            ['bash', 'csh', 'list', 'help', 'debug='])
    except getopt.error, e:
        usage(1, e)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-b', '--bash'):
            options.bash = 1
        elif opt in ('-c', '--csh'):
            options.csh = 1
        elif opt in ('-l', '--list'):
            options.olist = 1
        elif opt in ('-d', '--debug'):
            options.debug = arg

    return options, args

def set_vars(isy, *arg):
    # print "set_vars arg: ", arg
    for ar in arg:
        name, val  = str(ar).split('=')
        print "set ", name, " to ", val
        if str(val).isdigit:
            try:
                isy.var_set_value(name, val)
            except LookupError:
                print "bad Var name: ", ar
        else:
            print "bad Value: ", ar
    return

if __name__ == '__main__':

    options, arg = parseargs()
    myisy = ISY.Isy( debug=options.debug )

    if options.olist:
        list_vars(myisy)
    elif options.bash or options.csh:
        list_vars_bash(myisy, options.csh)

    if len(arg):
        set_vars(myisy, *arg)

