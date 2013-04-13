#!/usr/local/bin/python2.7



import ISY
import pprint
 
  
myisy= ISY.Isy(debug=2)
   
myisy.load_prog()


pfmt = "{:<5}{:<24} {:<5} {:<5}{!s:<5}"
print(pfmt.format("Id", "Node Name", "Stat", "Run", "Enabled"))
print(pfmt.format("-" * 4, "-" * 10, "-" * 4, "-" * 4,"-" * 4))
for p in myisy.prog_iter():
   if p.folder :
       print(pfmt.format(p.id, p.name, p.status, "-", "-"))
   else:
       print(pfmt.format(p.id, p.name, p.status, p.running, p.enabled))



