#!/usr/local/bin/python2.7
"""
    Call Soap API from command line 

    To reboot ISY :
	isy_sendcomm.py Reboot

    isy_sendcomm.py GetUserDirectory :
	prints XML of User Directory file list

"""

__author__ = "Peter Shipley"

import sys
import ISY

 
def callcomm(isy, *vargs) :


    args = vargs[0]
    if (len(args) == 0) :
	print "needs args"
	exit(0)

    comm = args.pop(0)

    kw = dict ()
    for var_arg in args :
	(arg_name, arg_val) = var_arg.split('=')

	# check we got two value names
	if (not arg_name) or (not arg_val):
	    warn("Invalid arg  : {0}".format(var_arg), RuntimeWarning)
	    continue

	kw[arg_name] = arg_val

    return isy.soapcomm(comm, **kw)

     

if __name__ == '__main__' :
    myisy = ISY.Isy( )
    r = callcomm(myisy, sys.argv[1:])
    print r
    exit(0)
