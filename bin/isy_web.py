#!/usr/local/bin/python2.7

"""

Simple example to List, Upload and download user webserver files from ISY


    {0} COMMAND [arg1 [arg2] ... ]


where command can be one owhere command can be one of :
    SEND : send / upload a file
    MKDIR : make directory
    RMDIR : remove / delete a directory
    RM : remove / delete a file
    DELETE : same as rm
    MV : move / rename a file or directory
    GET : get (download) a file
    DF : display free disk space
    LS : list files and directories
    LIST : same as ls
    DIR : same as ls

"""

import os
import sys
import ISY
from ISY.IsyClass import Isy, IsyGetArg
from ISY.IsyExceptionClass import IsyResponseError, IsyValueError
import pprint;

__doc__ = __doc__.format( os.path.basename(sys.argv[0])) 
def main(isy):

    # print "sys.argv[1:] = {!s}".format( len(sys.argv[1:]) )

    if len(sys.argv[1:]) == 0 :
	print_listing(isy)
	# print_listing_sort(isy)
	print_fsstat(isy)
    else :
	cmd = sys.argv.pop(1).upper()
	if (cmd == "SEND") :

	    srcfile = sys.argv.pop(1) 

	    if ( len(sys.argv) > 1 ) :
		dstfile = sys.argv.pop(1)
	    else :
		dstfile = os.path.basename(srcfile)

	    print "SEND {!s} {!s}".format(srcfile,dstfile)

	    res = isy.user_uploadfile(srcfile=srcfile, name=dstfile)
	    print "res = ", res
	elif cmd in [ "MKDIR", "MD" ] :
	    if ( len(sys.argv) > 1 ) :
		dstfile = sys.argv.pop(1)
		r = isy.user_mkdir(name=dstfile);
		print "r = ", r
	    else :
		print "Missing Arg"
	elif cmd in ["RMDIR" , "RD"] :
	    if ( len(sys.argv) > 1 ) :
		dstdir = sys.argv.pop(1)
		r = isy.user_rmdir(name=dstdir);
		print "r = ",r
	    else :
		print "Missing Arg"
	elif cmd in [ "RM", "DEL", "DELETE"] :
	    if ( len(sys.argv) > 1 ) :
		dstdir = sys.argv.pop(1)
		r = isy.user_rm(name=dstdir);
		print "r = ", r
	    else :
		print "Missing Arg"
	elif cmd in  ["MV", "RENAME"] :
	    if ( len(sys.argv) > 1 ) :
		old = sys.argv.pop(1)
		new = sys.argv.pop(1)
		r = isy.user_mv(name=old, newName=new);
		print "r = ",r
	    else :
		print "Missing Arg"
	elif cmd == "GET" :
	    if ( len(sys.argv) >= 1 ) :
		name = sys.argv.pop(1)
		r = isy.user_getfile(name=name);
		print "r = ", r
	    else :
		print "Missing Arg"
	elif cmd == "DF" :
	    print_fsstat(isy)
	elif cmd in ["LS", "LIST", "DIR"] :
	    print_listing_sort(isy) 
	    print_fsstat(isy)
	elif cmd == "HELP" :
	    help()
	    exit(0)
	else :
	    print "unknown command : {!s}".format(cmd)
	    help()
	    exit(0)


def print_listing_sort(isy) :
    """ print sorted file list """
    mytotal = 0
    mylist = dict()
    flist = isy.user_dir()
    # pprint.pprint(flist)
    for k, v in flist.items() :
	if ( k == 'dir') :
	    if isinstance(v, list) :
		for l in v :
		    if l["dir-name"] not in mylist :
			mylist[l["dir-name"]] = [ ]
	    else :
		if v["dir-name"] not in mylist :
		    mylist[v["dir-name"]] = [ ]
	elif ( k == 'file' ) :
	    if isinstance(v, list) :
		for l in v :
		    dir = os.path.dirname(l["file-name"]) 
		    if dir not in mylist :
			mylist[dir] = [ ]

		    mylist[dir].append( "\t{!s}\t{!s}".format(
			sizeof_fmt(int(l["file-size"])), l["file-name"]))
		    mytotal += int(l["file-size"])
	    else :
		dir = os.path.dirname(v["file-name"]) 
		if dir not in mylist :
		    mylist[dir] = [ ]
		mylist[dir].append( "\t{!s}\t{!s}".format(
			sizeof_fmt(int(v["file-size"])), v["file-name"]))
		mytotal += int(l["file-size"])
	else :
	    print "unknown list type : ", k
    #
    for key in sorted(mylist.iterkeys()):
	print key, ":"
	for l in mylist[key] :
	    print l
    print "Total:\t{:.1f}K".format( (float(mytotal) / 1024) )
    print "Total:\t{!s}".format( sizeof_fmt(mytotal) )

def print_listing(isy) :
#
    flist = isy.user_dir()
    # pprint.pprint(flist)
    for k, v in flist.items() :
	if ( k == 'dir') :
	    if isinstance(v, list) :
		for l in v :
		    print "dir\t{!s}".format(l["dir-name"])
	    else :
		print "dir\t{!s}".format(v["dir-name"])
	elif ( k == 'file' ) :
	    print type(k), type(v)
	    # print "k v = ", k, v
	    if isinstance(v, list) :
		for l in v :
		    print "file\t{!s}\t{!s}".format(l["file-size"], 
			l["file-name"])
	    else :
		print "file\t{!s}\t{!s}".format(v["file-size"], 
		    v["file-name"])
	else :
	    print "unknown list type : ", k

def sizeof_fmt(num):
    if num < 1024.0:
	return num
    for x in ['','KB','MB','GB','TB']:
	if num < 1024.0:
	    return "{:3.1f} {!s}".format(num, x)
	num /= 1024.0

def print_fsstat(isy) :
    #
    flist = isy.user_fsstat()
    # pprint.pprint(flist)
    print "free={!s}  used={!s} reserved={!s} total={!s}".format(
	sizeof_fmt(int(flist["free"])),
	sizeof_fmt(int(flist["used"])),
	sizeof_fmt(int(flist["reserved"])),
	sizeof_fmt(int(flist["total"])),
	)

def help():
    print >> sys.stderr, __doc__
 

if __name__=="__main__":

    r = IsyGetArg(sys.argv)

    myisy= ISY.Isy(debug=0x20,faststart=2,eventupdates=0)
	# addr=r[0], userl=r[1], userp=r[2] )
    main(myisy)
    exit(0)
