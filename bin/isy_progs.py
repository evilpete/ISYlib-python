#!/usr/local/bin/python2.7


import ISY
   
def list_progs(isy) :

    pfmt = "{:<5}{:<24} {:<5} {:<5}{!s:<5}"
    print(pfmt.format("Id", "Node Name", "Stat", "Run", "Enabled"))
    print(pfmt.format("-" * 4, "-" * 10, "-" * 4, "-" * 4,"-" * 4))
    for p in isy.prog_iter():
       if p.folder :
	   print(pfmt.format(p.id, p.name, p.status, "-", "-"))
       else:
	   print(pfmt.format(p.id, p.name, p.status, p.running, p.enabled))


if __name__ == '__main__' :
    myisy = ISY.Isy( )
    list_progs(myisy)
    exit(0)
