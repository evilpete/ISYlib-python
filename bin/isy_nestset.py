#!/usr/local/bin/python2.7



import nest
import sys
import ISY
from ISY.IsyExceptionClass import IsyValueError, IsyResponseError, IsyPropertyError

import time
# import pprint

from optparse import OptionParser
upass='nestpass'
uuser='nest_login@gmail.com'

def main() :


    parser = create_parser()
    (opts, args) = parser.parse_args()

    if (len(args)==0) or (args[0]=="help"):
        # help()
        sys.exit(-1)

    if (not opts.user) or (not opts.password):
        print "a --user and --password are needed"
        sys.exit(-1)

    # get Nest Values
    n = nest.Nest(uuser, upass, None, 0, "F")
    n.login()
    n.get_status()

    nest_values = dict ( )
    nest_values.update(n.status["structure"][n.structure_id])
    nest_values.update(n.status["shared"][n.serial] )
    nest_values.update(n.status["device"][n.serial] )

    myisy= ISY.Isy(debug=0, faststart=1)
    myisy.load_vars()

    targs = ( "1:38=current_temperature",
		"nest_humidity=current_humidity",
		"nest_away=away")

    for var_arg in targs :
	(isy_var, src_var) = var_arg.split('=')

	if src_var not in nest_values:
	    print "Invalid nest var :", src_var
	    next

	try :
	    myisy.var_set_value(isy_var, int(nest_values[src_var]))

	except IsyPropertyError :
	    print "invalid Isy Var :", isy_var
	    next
	except IsyValueError :
	    print "invalid value :", nest_values[src_var]
	    next
	except :
	    print("Unexpected error:", sys.exc_info()[0])
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

   parser.add_option("-u", "--user", dest="user",
                     help="username for nest.com", metavar="USER", default=uuser)

   parser.add_option("-p", "--password", dest="password",
                     help="password for nest.com", metavar="PASSWORD", default=upass)
   parser.add_option("-v", "--verbose", dest="verbose",
                     help="be verbose", metavar="VERBOSE", default=0)

   return parser



if __name__=="__main__":
    main()
    exit(0)
