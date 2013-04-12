#!/usr/local/bin/python2.7
"""
    a demo app that uses pynest to read values from the Nest
    and set vars in a ISY home automation device 
"""


import nest
import sys
import os
from warnings import warn

import time
# import pprint
from optparse import OptionParser

import ISY
from ISY.IsyExceptionClass import IsyValueError, IsyResponseError, IsyPropertyError


uuser=os.getenv('NEST_USER', None)
upass=os.getenv('NEST_PASS', None)

#
# Some of the following code was outright copy/pasted from pynest
#
def main() :

    parser = create_parser()
    (opts, args) = parser.parse_args()

    if (len(args)==0) or (args[0]=="help"):
        help()
        sys.exit(-1)

    if (not opts.uuser) or (not opts.upass):
        print "a --user and --password are needed"
        sys.exit(-1)

    # get Nest Values
    n = nest.Nest(opts.uuser, opts.upass, None, 0, "F")
    n.login()
    n.get_status()

    if (args[0]=="show") :
	n.show_status()
	exit(0)

    # consolidate data into a single dict
    nest_values = dict ( )
    nest_values.update(n.status["structure"][n.structure_id])
    nest_values.update(n.status["shared"][n.serial] )
    nest_values.update(n.status["device"][n.serial] )

    # faststart=1 don't load node data ( we not going to use it )
    myisy= ISY.Isy(debug=0, faststart=1)
    myisy.load_vars()

    # for debug
    targs = ( "1:38=current_temperature",
		"nest_humidity=current_humidity",
		"nest_away=away")

    for var_arg in args :
	(isy_var, src_var) = var_arg.split('=')

	if src_var not in nest_values:
	    print "Invalid nest var :", src_var
	    next

	try :
	    myisy.var_set_value(isy_var, int(nest_values[src_var]))

	except IsyPropertyError :
	    warn("Invalid Isy Var : {0}".format(isy_var), RuntimeWarning)
	    next
	except IsyValueError :
	    print "invalid value :", nest_values[src_var]
	    warn("Invalid value for ISY var: {0}".format(nest_values[src_var]),
		    RuntimeWarning)
	    next
	except :
	    print("Unexpected error:", sys.exc_info()[0])
	    warn("Unexpected error: {0}".format(sys.exc_info()[0]),
		    RuntimeWarning)
	    exit(0)
	else :
	    if opts.verbose :
		print isy_var,"=", int(nest_values[src_var])




#    if "$timestamp" in shared :
#	ti = shared["$timestamp"] // 1000
#	sha_time = time.strftime("%m%d%H%M%S", time.localtime(ti)).lstrip('0')
#	print "shared timestamp", shared["$timestamp"], time.ctime(ti), sha_time
#


def create_parser():
   parser = OptionParser(usage="isy_nest [options] isy_var=nest_var ",
        description="Commands: fan temp",
        version="unknown")

   parser.add_option("-u", "--user", dest="uuser",
                     help="username for nest.com", metavar="USER", default=uuser)
   parser.add_option("-p", "--password", dest="upass",
                     help="password for nest.com", metavar="PASSWORD", default=upass)
   parser.add_option("-c", "--celsius", dest="celsius", action="store_true", default=False,
                     help="use celsius instead of farenheit")
   parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
                     help="Be verbose")

   parser.add_option("-s", "--serial", dest="serial", default=None,
                     help="optional, specify serial number of nest thermostat to talk to")

   parser.add_option("-i", "--index", dest="index", default=0, type="int",
                     help="optional, specify index number of nest to talk to")

   return parser

def help():
    print "syntax: isy_nestset [options] isyvar=nestvar .... "
    print "options:"
    print "   --user <username>      ... username on nest.com"
    print "   --password <password>  ... password on nest.com"
    print "   --celsius              ... use celsius (the default is farenheit)"
    print "   --serial <number>      ... optional, specify serial number of nest to use"
    print "   --index <number>       ... optional, 0-based index of nest"
    print "                                (use --serial or --index, but not both)"
    print
    print "commands: isyvar=nestvar, show, help"
    print "    show                  ... show available nest vars"
    print "    help                  ... print this help"
    print
    print "    home_temp=current_temperature"
    print "                          ... set the var on the isy named 'home_temp'"
    print "                            to the value of the nest current_temperature"
    print "    Note: the varable has to preexist on the ISY device "
    print
    print "examples:"
    print "    nest.py --user joe@user.com --password swordfish home_temp=current_temperature"
    print "    nest.py --user joe@user.com --password swordfish show"


if __name__=="__main__":
    main()
    exit(0)
