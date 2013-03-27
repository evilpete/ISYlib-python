#!/usr/local/bin/python2.7

import ISY


def list_nodes(myisy) :
    print "%-20s %-12s\t%s" % ("Node Name", "Address", "Status")
    print "%-20s %-12s\t%s" % ("---------", "-------", "------")
    for nod in myisy :
       if nod.type == "scene" :
	   #print "%-20s %-12s\t%s" % (nod.name, nod.address, nod.members )
	   print "%-20s %-12s\t%s" % (nod.name, nod.address, "-")
       else :
	   print "%-20s %-12s\t%s" % (nod.name, nod.address, nod.formatted)

if __name__ == '__main__' :
    myisy = ISY.Isy( )
    list_nodes(myisy)

