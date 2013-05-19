#!/usr/local/bin/python2.7

"""

Simple example to send a WoL to a registared system on the ISY

if this script is call without any arg 
we print a list of network resources systems


"""

import sys
import ISY
from ISY.IsyExceptionClass import IsyResponseError, IsyValueError

# import pprint
 
  
myisy= ISY.Isy(debug=0)
   
myisy.load_net_resource()

if len(sys.argv[1:]) > 0:
    for a in sys.argv[1:] :
	try :
	    myisy.net_resource_run(a)
	except (IsyValueError, IsyResponseError), errormsg :
	    print "problem calling ISY network resource to {!s} : {!s}".format(a, errormsg)
	    continue
	else :
	    print "Net resource sent to {!s}".format(a)
else :
    pfmt = "{:<5}{:<16} {:<20}"
    print(pfmt.format("Id", "Name", "Addr"))
    print(pfmt.format("-" * 4, "-" * 20, "-" * 20))
    for r in myisy.net_resource_iter():
       #pprint.pprint(r)
       if "id" in r :
	   print(pfmt.format(r['id'], r['name'], r['ControlInfo']['host']))



