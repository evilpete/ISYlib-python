#!/usr/bin/env python
"""
    A simple example showing how
    to obtain and print status of every node
"""

__author__ = "Peter Shipley"

import ISY


def list_nodes(isy):
    """ iter though Isy Class object and print returned
        node's infomation
    """
    if "-l" in myisy.unknown_args:
        pfmt = "{:<22} {:>12}\t{:<12}{!s:<12} {!s:}"
    else:
        pfmt = "{:<22} {:>12}\t{:<12}{!s:<12}"

    print(pfmt.format("Node Name", "Address", "Status", "Enabled", "Path"))
    print(pfmt.format("---------", "-------", "------", "------", "----"))
    for nod in isy:
        if nod.objtype == "scene":
            print(pfmt.format(nod.name, nod.address, "-", "-", "-"))
        else:
            print(pfmt.format(nod.name, nod.address,
                    nod.formatted, nod.enabled, nod.path))


if __name__ == '__main__':
    myisy = ISY.Isy(parsearg=1) # debug=0x80
    list_nodes(myisy)
    exit(0)

