#!/usr/local/bin/python2.7

import ISY


def list_nodes(myisy) :
    pfmt = "{:<20} {:<12}\t{:<12}"
    print pfmt.format("Node Name", "Address", "Status")
    print pfmt.format("---------", "-------", "------")
    for nod in myisy :
       if nod.type == "scene" :
	   print pfmt.format(nod.name, nod.address, "-")
       else :
	   print pfmt.format(nod.name, nod.address, nod.formatted)
       # print " members : ", len(nod.members_list())

if __name__ == '__main__' :
    myisy = ISY.Isy( )
    list_nodes(myisy)

