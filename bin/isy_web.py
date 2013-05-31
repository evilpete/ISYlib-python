#!/usr/local/bin/python2.7

"""

Simple example to Lisst, Upload and download user webserver files from ISY

if this script is call without any arg 
we print a list of files

if we have any args we treat them as registared WoL Id's
and attempt to send a WoL packet 

"""

import os
import sys
import ISY
from ISY.IsyExceptionClass import IsyResponseError, IsyValueError
import pprint;
 
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
	elif cmd == "MKDIR" :
	    if ( len(sys.argv) > 1 ) :
		dstfile = sys.argv.pop(1)
		isy.user_mkdir(name=dstfile);
	    else :
		print "Missing Arg"
	elif cmd == "RMDIR" :
	    if ( len(sys.argv) > 1 ) :
		dstdir = sys.argv.pop(1)
		isy.user_rmdir(name=dstdir);
	    else :
		print "Missing Arg"
	elif cmd == "RM" :
	    if ( len(sys.argv) > 1 ) :
		dstdir = sys.argv.pop(1)
		isy.user_rm(name=dstdir);
	    else :
		print "Missing Arg"
	elif cmd == "MV" :
	    if ( len(sys.argv) > 1 ) :
		old = sys.argv.pop(1)
		new = sys.argv.pop(1)
		isy.user_mv(name=old, newName=new);
	    else :
		print "Missing Arg"
	elif cmd == "GET" :
	    if ( len(sys.argv) >= 1 ) :
		name = sys.argv.pop(1)
		isy.user_getfile(name=name);
	    else :
		print "Missing Arg"
	elif cmd in ["LS", "LIST", "DIR"] :
	    print_listing_sort(isy) 
	    print_fsstat(isy)
	else :
	    print "unknown command : {!s}".format(cmd)


def print_listing_sort(isy) :
    """ print sorted file list """
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
			l["file-size"], l["file-name"]))
	    else :
		dir = os.path.dirname(v["file-name"]) 
		if dir not in mylist :
			mylist[dir] = [ ]
		mylist[dir].append( "\t{!s}\t{!s}".format(
			v["file-size"], v["file-name"]))
	else :
	    print "unknown list type : ", k
    #
    for key in sorted(mylist.iterkeys()):
	print key, ":"
	for l in mylist[key] :
	    print l

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

def print_fsstat(isy) :
    #
    flist = isy.user_fsstat()
    # pprint.pprint(flist)
    print "free={:.2f}K  used={:.2f}K reserved={:.2f}K total={:.2f}M".format(
	( float(flist["free"]) / (1024**2)),
	( float(flist["used"]) / (1024**2)),
	( float(flist["reserved"]) / (1024**2)),
	( float(flist["total"]) / (1024**2)),
	)


# {'bad': '0',
# 'free': '870971802',
# 'reserved': '98748006',
# 'total': '987480064',
# 'used': '17760256'}
# {'dir': {'dir-name': '/USER/WEB'},
# 'file': {'file-name': '/USER/WEB/X10.HTM', 'file-size': '324'}}



if __name__=="__main__":
    myisy= ISY.Isy(debug=0x20,faststart=2,eventupdates=0)
    main(myisy)
    exit(0)
