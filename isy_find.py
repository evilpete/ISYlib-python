#!/usr/local/bin/python2.7

# import ISY
from  ISY.IsyDiscover import isy_discover


def list_units() :
    fmt = "%-25s %-25s %s"
    print fmt % ("Device Name", "Device Number", "URL Address" )
    print fmt % ("-" * 20, "-" * 20, "-" * 20 )
    r = isy_discover(timeout=10);
    for unit in r.itervalues() :
	print fmt % ( unit['friendlyName'], unit['UDN'], unit['URLBase']  )


if __name__ == '__main__' :
    list_units()

