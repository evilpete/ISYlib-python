#!/usr/bin/env python

__author__ = "Peter Shipley"

#
#  quick hack to check x10 address usage
#
#  Scan log history
#  Read Node configs
#
#  report:
#       All active X10 addresses
#       All addresses from Registared Nodes
#
#       Any X10 addresses  used but not assocated with Registared Nodes
#
# TODO : add option


#
#
from ISY.IsyClass import Isy, log_time_offset
from ISY.IsyEventData import LOG_USERID, LOG_TYPES

import sys


time_const=2208988800;

def main(isy):

    addr_received = set()
    addr_used = set()
    addr_known = set()
    addr_unknown = set()
    known_housecodes = set()

    header = [ "Node", "Control", "Action", "Time", "UID", "Log Type" ]

    for nod in isy:

        a = str(nod.address).split(' ')
        # or .type = 113.X.X.X
        if a[0] == 'FF':
            house = chr( 64 + int(a[1], 16) )
            unit = str(int(a[2], 16))
            node = house + unit
            addr_known.add(node)
            known_housecodes.add(house)

    print "addr_known : ", str(", ").join(sorted(addr_known))


    for log_line in isy.log_iter():
        col = str(log_line).split("\t")

        if col[0] == "X10":
            #print col[1]
            if int(col[4]) == 0:
                addr_received.add(col[1])
            else:
                addr_used.add(col[1])

    print "addr_received = ", str(", ").join(sorted(addr_received))
    print "addr_used = ", str(", ").join(sorted(addr_used))

    addr_unknown = addr_received.union(addr_used) - addr_known
    addr_unknown -= known_housecodes

    print "addr_unknown = ", str(", ").join(sorted(addr_unknown))




if __name__ == '__main__':
    myisy = Isy(parsearg=1)
    main(myisy)
    exit(0)

