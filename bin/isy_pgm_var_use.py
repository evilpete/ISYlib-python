#!/usr/local/bin/python2.7
#
#  quick hack to check what ISY vars are in use by which programs
#
#  then report :
#	program name and var ids used
#
#	summary list of used vars by ids
#	summary vars only referanced once 
#	summary list of unused vars by ids
#	summary list of unused vars by name
#
# TODO : add options
#

opt_fullpath = True
opt_skipnovars = True

__author__ = "Peter Shipley"

import xml.etree.ElementTree as ET


import ISY
   
def list_prog_vars(isy) :

    var_known_set = set(isy.var_ids())
    var_used_all = set()

    var_use_count = dict()

    if opt_fullpath :
	name_width = 45
    else :
	name_width = 24
    for p in isy.prog_iter():
	var_used = [ ]

	if p.id == '0001' :
	    continue

	src_xml = isy.prog_get_src(p.id)

	src_info = ET.fromstring(src_xml)

	for v in src_info.iter("var") :
	    vid = v.attrib["type"] + ":" + v.attrib["id"]
	    var_used.append(vid)
	    var_use_count[vid] = var_use_count.get(vid, 0) + 1

	var_used_set = set(var_used)
	var_list = sorted(var_used_set)
	var_used_all.update(var_used_set)

	if p.parentId == '0001' or opt_fullpath == False  :
	    pname = p.name
	else :
	    pname = p.name
	    pgm = isy.get_prog(p.parentId)
	    while pgm.id != '0001' :
		pname = pgm.name + "/" + pname 
		pgm = isy.get_prog(pgm.parentId)
	    
	if len(var_list) > 0 or  opt_skipnovars != True :
	    print "{:<5}{:<{namew}} {!s}".format(p.id, pname, ", ".join(var_list), namew=name_width),

	    missing_var_set = var_used_set - var_known_set
	    if missing_var_set :
		print "( bad : ",  str(", ").join(missing_var_set), " ) ",
	    print

    var_used_once_set = set()
    for k, v in var_use_count.items() :
	if v == 1 :
	    var_used_once_set.add(k)


    print "\nUsed var Ids (", len(var_used_all), "): ",
    print str(", ").join(sorted(var_used_all, None, varkey))

    if var_used_once_set :
	print "\nUsed var once Ids (", len(var_used_once_set), "): ",
	print str(", ").join(sorted(var_used_once_set, None, varkey))


    unused_var_set = var_known_set - var_used_all

    unused_var_set_sorted = sorted(unused_var_set,None,varkey)
    print "\nUnused var Ids (", len(unused_var_set), "): ",
    print str(", ").join(unused_var_set_sorted)


    print "\nUnused var Names (", len(unused_var_set), "): ",
    print str(", ").join( [isy._vardict[el]["name"] for el in unused_var_set_sorted])


def varkey(vstr):
     vkeys = vstr.split(':')
     varkval = (int(vkeys[0]) * 100) + int(vkeys[1])
     return str(varkval)



if __name__ == '__main__' :
    myisy = ISY.Isy(faststart=2,eventupdates=0)
    myisy.load_vars()
    myisy.load_prog()
    list_prog_vars(myisy)
    exit(0)
