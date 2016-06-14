#!/usr/bin/env python

__author__ = "Peter Shipley"
#
#  quick hack to check what ISY vars are in use by which programs
#
#  then report:
#       program name and var ids used
#
#       summary list of used vars by ids
#       summary vars only referanced once
#       summary list of unused vars by ids
#       summary list of unused vars by name
#
# TODO : add options
#

# print program's full path include parent folder
opt_fullpath = True
# Skip program that don't use vars
opt_skipnovars = True


import xml.etree.ElementTree as ET

import ISY

def list_prog_vars(isy):

    # get a list of all var Ids and store them as a set
    var_known_set = set(isy.var_ids())

    # a set for all referanced cars
    var_used_all = set()

    var_use_count = dict()

    if opt_fullpath:
        name_width = 45
    else:
        name_width = 24

    # iterate though all programs and program folders
    for p in isy.prog_iter():

        var_used = [ ]

        # skip root folder.
        if p.id == '0001':
            continue

        # get D2D src for program
        src_xml = isy.prog_get_src(p.id)

        # parse the D2D code ( XML format )
        src_info = ET.fromstring(src_xml)

        # find all the referances to program vars
        # and store them in an array
        for v in src_info.iter("var"):
            vid = v.attrib["type"] + ":" + v.attrib["id"]
            var_used.append(vid)
            var_use_count[vid] = var_use_count.get(vid, 0) + 1

        # convert the array into a set
        var_used_set = set(var_used)


        var_list = sorted(var_used_set)

        # add this set to total used set
        var_used_all.update(var_used_set)

        # referance program by name or full path
        if p.parentId == '0001' or opt_fullpath == False :
            pname = p.name
        else:
            pname = p.path


        # if program has vars, print name and list vars it contains.
        if len(var_list) > 0 or  opt_skipnovars != True:
            print "{:<5}{:<{namew}} {!s}".format(p.id, pname, ", ".join(var_list), namew=name_width),

            # check it any of the referanced vars are missing from the system var list
            # if so report this
            missing_var_set = var_used_set - var_known_set
            if missing_var_set:
                print "( bad : ",  str(", ").join(missing_var_set), " ) ",
            print


    # not that we have searched all the programs...

    # report vars that are referanced only once...
    var_used_once_set = set()
    for k, v in var_use_count.items():
        if v == 1:
            var_used_once_set.add(k)


    # print all vars that are used.
    print "\nUsed var Ids (", len(var_used_all), "): ",
    print str(", ").join(sorted(var_used_all, None, varkey))

    if var_used_once_set:
        print "\nUsed var once Ids (", len(var_used_once_set), "): ",
        print str(", ").join(sorted(var_used_once_set, None, varkey))


    unused_var_set = var_known_set - var_used_all

    # print var Ids that exist that are not referanced
    unused_var_set_sorted = sorted(unused_var_set,None,varkey)
    print "\nUnused var Ids (", len(unused_var_set), "): ",
    print str(", ").join(unused_var_set_sorted)


    # also print the vars by name
    print "\nUnused var Names (", len(unused_var_set), "): ",
    print str(", ").join( [isy._vardict[el]["name"] for el in unused_var_set_sorted])


# funtion call for sorting var Ids ( in the form of 1:23 )
def varkey(vstr):
     vkeys = vstr.split(':')
     varkval = (int(vkeys[0]) * 100) + int(vkeys[1])
     return str(varkval)



if __name__ == '__main__':

    # open connection to ISY
    # don't preload node, dont subscribe to updates
    #
    # get login / pass from from Env.
    myisy = ISY.Isy(faststart=2,eventupdates=0,parsearg=1)

    # preload programs and vars
    myisy.load_vars()
    myisy.load_prog()

    list_prog_vars(myisy)

    exit(0)
