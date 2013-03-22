#!/usr/local/bin/python2.7

import ISY


def list_units() :
    fmt = "%-25s %-25s %s"
    print fmt % ("Device Name", "Device Number", "Address" )
    print fmt % ("-" * 20, "-" * 20, "-" * 20 )
    r = ISY.isy_discover();
    for unit in r.itervalues() :
	print fmt % ( unit['friendlyName'], unit['UDN'], unit['URLBase']  )


if __name__ == '__main__' :
    list_units()

