#!/usr/bin/env python

"""

Simple example to List, Upload and download user webserver files from ISY


    {0} COMMAND [arg1 [arg2] ... ]

optional arguments:
        -h, --help           show this help message and exit
        -d [DEBUG]]          debug options
        -a ADDR              hostname or IP device
        -u USER              Admin Username
        -p PASS             Admin Password


where command can be one owhere command can be one of:
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

All non-absolute remote filenames are assumed to be relative to /USER/WEB

"""

__author__ = "Peter Shipley"

import os
import sys
import ISY
# from ISY.IsyClass import Isy
# from ISY.IsyExceptionClass import IsyResponseError, IsyValueError
# import pprint

__doc__ = __doc__.format( os.path.basename(sys.argv[0]))
def main(isy):

    systemconf = 0

    # print "sys.argv[1:] = {!s}".format( len(sys.argv[1:]) )

    # print "unknown_args : ", isy.unknown_args
    # print "sys.argv : ", sys.argv
    argv = isy.unknown_args[:]
    # print "argv : ", argv

    if len(argv) == 0:
        print_listing(isy)
        # print_listing_sort(isy)
        print_fsstat(isy)
    else:

        if argv.pop in ["-s", "--system"]:
            _ = argv.pop(0)
            systemconf = 1

        cmd = argv.pop(0).upper()
        # print "cmd = ", cmd
        if cmd in ["SEND", "PUT"]:

            srcfile = argv.pop(0)

            if ( len(argv) > 0 ):
                dstfile = argv.pop(0)
            else:
                dstfile = os.path.basename(srcfile)

            print "SEND {!s} {!s}".format(srcfile, dstfile)

            res = isy.user_uploadfile(srcfile=srcfile, name=dstfile)
#           if res:
#               print "res = ", res
        elif cmd in [ "MKDIR", "MD" ]:
            if ( len(argv) > 0 ):
                dstfile = argv.pop(0)
                res = isy.user_mkdir(name=dstfile)
#               if res:
#                   print "res = ", res
            else:
                print "Missing Arg:\n\t{!s} <dirname>".format(cmd)
        elif cmd in ["RMDIR" , "RD"]:
            if ( len(argv) > 0 ):
                dstdir = argv.pop(0)
                res = isy.user_rmdir(name=dstdir)
                #if res:
                #    print "res = ", res
            else:
                print "Missing Arg:\n\t{!s} <dirname>".format(cmd)
        elif cmd in [ "RM", "DEL", "DELETE"]:
            if ( len(argv) > 0 ):
                dstdir = argv.pop(0)
                res = isy.user_rm(name=dstdir)
                # if res:
                 #    print "res = ", res
            else:
                print "Missing Arg:\n\t{!s} <filename>".format(cmd)
        elif cmd in ["MV", "RENAME"]:
            if ( len(argv) > 1 ):
                old = argv.pop(0)
                new = argv.pop(0)
                res = isy.user_mv(name=old, newName=new)
#               if res:
#                   print "res = ", res
            else:
                print "Missing Arg:\n\t{!s} <filename> <filename>".format(cmd)
        elif cmd == "GET":
            if ( len(argv) < 1 ):
                print "Missing Arg:\n\t{!s} <remote_filename> [local_filename]".format(cmd)
                exit(0)

            name = argv.pop(0)

            if ( len(argv) > 0 ):
                dstfile = argv.pop(0)
            elif str(name).upper().startswith("/"):
                dstfile = os.path.basename(name)
            else:
                dstfile = name

            if systemconf:
                res = self.soapcomm("GetSysConf", name=varpath)
            else:
                res = isy.user_getfile(name=name)

            with open(dstfile, 'w') as fh:
                fh.write(res)
            print "{!s} bytes written to {!s}".format(len(res), dstfile)

        elif cmd == "DF":
            print_fsstat(isy)
        elif cmd in ["LS", "LIST", "DIR"]:
            print_listing_sort(isy)
            print_fsstat(isy)
        elif cmd == "HELP":
            help()
            exit(0)
        else:
            print "unknown command : {!s}".format(cmd)
            help()
            exit(0)


def print_listing_sort(isy):
    """ print sorted file list """
    mytotal = 0
    mylist = dict()
    flist = isy.user_dir()
    # pprint.pprint(flist)
    for key, val in flist.items():
        if ( key == 'dir'):
            if isinstance(val, list):
                for l in val:
                    if l["dir-name"] not in mylist:
                        mylist[l["dir-name"]] = [ ]
            else:
                if val["dir-name"] not in mylist:
                    mylist[val["dir-name"]] = [ ]
        elif ( key == 'file' ):
            if isinstance(val, list):
                for l in val:
                    dirn = os.path.dirname(l["file-name"])
                    if dirn not in mylist:
                        mylist[dirn] = [ ]

                    mylist[dirn].append( "\t{!s}\t{!s}".format(
                        sizeof_fmt(int(l["file-size"])), l["file-name"]))
                    mytotal += int(l["file-size"])
            else:
                dirn = os.path.dirname(val["file-name"])
                if dirn not in mylist:
                    mylist[dirn] = [ ]
                mylist[dirn].append( "\t{!s}\t{!s}".format(
                        sizeof_fmt(int(val["file-size"])), val["file-name"]))
                mytotal += int(l["file-size"])
        else:
            print "unknown list type : ", key
    #
    for key in sorted(mylist.iterkeys()):
        print key, ":"
        for l in mylist[key]:
            print l
    # print "Total:\t{:.1f}K".format( (float(mytotal) / 1024) )
    print "Total:\t{!s}".format( sizeof_fmt(mytotal) )

def print_listing(isy):
#
    flist = isy.user_dir()
    # pprint.pprint(flist)
    for key, val in flist.items():
        if ( key == 'dir'):
            if isinstance(val, list):
                for l in val:
                    print "dir\t{!s}".format(l["dir-name"])
            else:
                print "dir\t{!s}".format(val["dir-name"])
        elif ( key == 'file' ):
            # print type(key), type(val)
            # print "key val = ", key, val
            if isinstance(val, list):
                for l in val:
                    print "file\t{!s}\t{!s}".format(l["file-size"],
                        l["file-name"])
            else:
                print "file\t{!s}\t{!s}".format(val["file-size"],
                    val["file-name"])
        else:
            print "unknown list type : ", key

def sizeof_fmt(num):
    if num < 1024.0:
        return num
    for x in ['', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "{:3.1f} {!s}".format(num, x)
        num /= 1024.0

def print_fsstat(isy):
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


if __name__ == "__main__":

    myisy = ISY.Isy(faststart=2, eventupdates=0, parsearg=1)
    main(myisy)
    exit(0)
