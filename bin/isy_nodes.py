#!/usr/local/bin/python2.7
"""
    A simple example showing how
    to obtain and print status of every node
"""

import ISY


def list_nodes(isy) :
    """ iter though Isy Class object and print returned
	node's infomation
    """
    pfmt = "{:<20} {:<12}\t{:<12}{!s:<12}"
    print(pfmt.format("Node Name", "Address", "Status", "Enabled"))
    print(pfmt.format("---------", "-------", "------", "------"))
    for nod in isy :
        if nod.type == "scene" :
            print(pfmt.format(nod.name, nod.address, "-", "-"))
        else :
            print(pfmt.format(nod.name, nod.address, 
		    nod.formatted, nod.enabled))

if __name__ == '__main__' :
    MYISY = ISY.Isy( )
    list_nodes(MYISY)

