#!/usr/bin/env python

from __future__ import print_function

__author__ = "Peter Shipley"
__license__ = "BSD"


# Simple example
#
#   This script listens for Upnp advertisements from any local ISY
#   unit and prints results
#


from  ISY.IsyDiscover import isy_discover

def list_units():
    fmt = "%-25s %-25s %s"
    print(fmt % ("Device Name", "Device Number", "URL Address" ))
    print(fmt % ("-" * 20, "-" * 20, "-" * 20 ))

    # wait upto 5 seconds or after you have discovered two unit
    r = isy_discover(timeout=5, count=2)
    for key, unit in r.items():
        print(fmt % ( unit['friendlyName'], unit['UDN'], unit['URLBase']  ))


if __name__ == '__main__':
    list_units()
    exit(0)

