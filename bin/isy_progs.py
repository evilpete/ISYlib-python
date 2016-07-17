#!/usr/bin/env python


__author__ = "Peter Shipley"


import ISY

def list_progs(isy):

    pfmt = "{:<5}{:<24} {:<5} {:<5}{!s:<6} {!s:}"
    print(pfmt.format("Id", "Node Name", "Stat", "Run", "Enabled", "Path"))
    print(pfmt.format("-" * 4, "-" * 10, "-" * 4, "-" * 4,"-" * 4, "-" * 4))
    for p in isy.prog_iter():
       if p.folder:
           print(pfmt.format(p.id, p.name, p.status, "-", "-", p.path + "/" ))
       else:
           print(pfmt.format(p.id, p.name, p.status, p.running, p.enabled, p.path))


if __name__ == '__main__':
    myisy = ISY.Isy( parsearg=1 )
    list_progs(myisy)
    exit(0)
