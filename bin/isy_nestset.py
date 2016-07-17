#!/usr/bin/env python
"""
    a demo app that uses pynest to read values from the Nest
    and set vars in a ISY home automation device

    See also : https://github.com/smbaker/pynest
               https://github.com/evilpete/ISYlib-python

"""
__author__ = "Peter Shipley"


try:
    import nest_thermostat as nest
except ImportError as e:
    print "Package nest-thermostat required :", \
            "https://pypi.python.org/pypi/nest-thermostat"
    exit(1)

#import nest
import sys
import os
from warnings import warn

import pprint
from optparse import OptionParser

import ISY
from ISY.IsyExceptionClass import IsyValueError, IsyResponseError, IsyPropertyError


uuser=os.getenv('NEST_USER', None)
upass=os.getenv('NEST_PASS', None)

temperature_vars = ( "away_temperature_high", "away_temperature_low",
                    "current_temperature", "target_temperature",
                    "target_temperature_high", "target_temperature_low",
                    "temperature_lock_high_temp", "temperature_lock_low_temp",
                    "upper_safety_temp", "lower_safety_temp" )


#
# Some of the following code was outright copy/pasted from pynest
#
def main():

    parser = create_parser()
    (opts, args) = parser.parse_args()

    if (len(args)==0) or (args[0]=="help"):
        help_txt()
        sys.exit(-1)

    if (not opts.uuser) or (not opts.upass):
        print "a --user and --password are needed"
        sys.exit(-1)

    # get Nest Values
    n = nest.Nest(opts.uuser, opts.upass, None, 0, "F")
    n.login()
    n.get_status()

    if (args[0]=="show"):
        n.show_status()
        exit(0)

    # consolidate data into a single dict
    nest_values = dict ( )
    nest_values.update(n.status["structure"][n.structure_id])
    nest_values.update(n.status["shared"][n.serial] )
    nest_values.update(n.status["device"][n.serial] )

    if (args[0]=="dump"):
        pprint.pprint(nest_values)
        exit(0)

    # faststart=1 don't load node data ( we not going to use it )
    myisy= ISY.Isy(debug=0, faststart=1)


    # not really needed but will speed up the first call
    #myisy.load_vars()

    auto_args = ( "nest_temp=current_temperature",
                "nest_humidity=current_humidity",
                "nest_away=away")

    if (args[0]=="auto"):
        args.pop(0)
        args.extend(auto_args)

    for var_arg in args:
        (isy_var, src_var) = var_arg.split('=')

        # check we got two value names
        if (not isy_var) or (not src_var):
            warn("Invalid arg  : {0}".format(var_arg), RuntimeWarning)
            continue

        # check if net value name is valid
        if src_var not in nest_values:
            warn("Invalid Nest Value : {0}".format(isy_var), RuntimeWarning)
            continue

        # convert temperature to F
        # we can't convert in place since the value may be used twice
        if src_var in temperature_vars and not opts.celsius:
            set_value = nest_values[src_var] *1.8 + 32.0
        else:
            set_value = nest_values[src_var]


        try:
            # this will raise an error if there is a problem with name or set_value
            myisy.var_set_value(isy_var, int(set_value))

        except IsyPropertyError:
            warn("Invalid Isy Var : {0}".format(isy_var), RuntimeWarning)
            continue
        except (IsyValueError , ValueError):
            print "invalid value :", nest_values[src_var]
            warn("Invalid value for ISY var: {0}".format(set_value),
                    RuntimeWarning)
            continue
        except:
            print("Unexpected error:", sys.exc_info()[0])
            warn("Unexpected error: {0}".format(sys.exc_info()[0]),
                    RuntimeWarning)
            exit(0)
        else:
            if opts.verbose:
                print isy_var,"=", int(set_value)

    # end of main
    return



# convert time stamp into someting we can pass along
#    if src_var == "$timestamp":
#       ti = nest_values["$timestamp"] // 1000
#       set_value = time.strftime("%m%d%H%M%S", time.localtime(ti)).lstrip('0')
#       print "shared timestamp", nest_values["$timestamp"],
#              time.ctime(ti), set_value
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

def help_txt():
    print "syntax: isy_nestset [options] isyvar=nestvar .... "
    print "options:"
    print "   --user <username>      ... username on nest.com"
    print "   --password <password>  ... password on nest.com"
    print "   --celsius              ... use celsius (the default is farenheit)"
    print "   --serial <number>      ... optional, specify serial number of nest to use"
    print "   --index <number>       ... optional, 0-based index of nest"
    print "                                (use --serial or --index, but not both)"
    print "   -v                     ... verbose"
    print
    print "commands: isyvar=nestvar, show, help"
    print "    show                  ... show available nest vars"
    print "    help                  ... print this help"
    print "    auto                  ... set vars nest_awaynest_humidity nest_temp in ISY"
    print
    print "    home_temp=current_temperature"
    print "                          ... set the var on the isy named 'home_temp'"
    print "                            to the value of the nest current_temperature"
    print "    Note: the varable has to preexist on the ISY device "
    print
    print "examples:"
    print "    isy_nestset.py --user joe@user.com --password swordfish home_temp=current_temperature"
    print "    isy_nestset.py --user joe@user.com --password swordfish show"

    # end of help
    return

if __name__=="__main__":
    main()
    exit(0)
