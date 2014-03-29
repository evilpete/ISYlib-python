

import os
import ISY
import zipfile
import pprint
import xml.etree.ElementTree as ET
import time
import tempfile
from ISY.IsyUtilClass import et2d
import argparse

dirset = set()
fileset = set()
#folder = None
outfile = None
verbose = 0

from ISY.IsyExceptionClass import IsySoapError


#ISY-Backup.v4.1.2__Fri 2014.03.14 17.46.52.zip
#uuid.00.21.b9.00.e7.08.zip*

def parse_args(isy) :
#    global folder
    global outfile
    global verbose

    parser = isy.parser

    # parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--outfile", dest="outfile",
                        help="output file")

#    parser.add_argument("-f", "--folder", dest="folder",
#                       help="output folder")

    parser.add_argument('--verbose', '-v', action='count')

    args, unknown_args = parser.parse_known_args()

#    if args.outfile and args.folder :
#       print "you can't use both file and folder"
#       parser.print_help()
#       exit(0)

    print args
    outfile = args.outfile
    verbose = args.verbose
#    folder = args.folder


def zipit(isy) :
    global outfile
    global verbose

    parse_args(isy)

   #  if folder is None :
    if outfile is None :
        time_str = time.strftime("%a_%Y.%m.%d_%H.%M.%S" , time.localtime())
        outfile = "ISY-Backup.v{0}_{1}.zip".format(isy.app_version, time_str)
    elif not outfile.endswith((".zip", ".ZIP")) :
        outfile = outfile + ".zip"

    backupid = "uuid.{0}.zip".format(isy.id)

    zip_get_conf(isy)

    zip_get_userweb(isy)

    zip_get_ui_conf(isy)

    tf = tempfile.NamedTemporaryFile(delete=False)
    zf = zipfile.ZipFile(tf, "w")

    for d in dirset :
        add_dir(isy, zf, d)

    for f in fileset :
        add_file(isy, zf, f)

    zf.close()
    tf.close()

    zff = zipfile.ZipFile(outfile, "w")
    zff.write(tf.name, backupid)
    zff.close()
    os.unlink(tf.name)
    print "Backup completed"
    print "output file = ", outfile


def zip_get_ui_conf(isy) :
    dirset.add("/WEB/CONF")
    fileset.add("/WEB/CONF/CAMS.JSN")
    fileset.add("/WEB/CONF/CAMS.J")


def zip_get_conf(isy) :
    global dirset
    global fileset

    dat = isy.soapcomm("GetSysConfFiles")
    flist = et2d(ET.fromstring(dat))
    # pprint.pprint(flist)

    if "dir-name" in flist :
        if isinstance(flist['dir-name'], list) :
            for d in flist['dir-name'] :
                if d.startswith("/") :
                    dirset.add(d)
                else :
                    dirset.add("/CONF/" + d)
        else :
            if flist['dir-name'].startswith("/") :
                dirset.add(flist['dir-name'])
            else :
                dirset.add("/CONF/" + flist['dir-name'])

    if "entry" in flist :
        if isinstance(flist['entry'], list) :
            for f in flist['entry'] :
                fileset.add("/CONF/" + f)
        else :
            fileset.add("/CONF" + flist["entry"])


def zip_get_userweb(isy) :
    global dirset
    global fileset

    dat = isy.soapcomm("GetUserDirectory")
    flist = et2d(ET.fromstring(dat))

    # pprint.pprint(flist)

    if "dir" in flist :
        if isinstance(flist['dir'], list) :
            for d in flist['dir'] :
                dirset.add(d["dir-name"])
        else :
            dirset.add(flist['dir']["dir-name"])

    if "dir" in flist :
        if isinstance(flist['dir'], list) :
            for d in flist['dir'] :
                dirset.add(d["dir-name"])
        else :
            dirset.add(flist['dir']["dir-name"])

    if "file" in flist :
        if isinstance(flist['file'], list) :
            for f in flist['file'] :
                fileset.add(f["file-name"])
        else :
            fileset.add(flist['file']["file-name"])


def add_file(isy, zf, fpath) :
    global verbose

    if not fpath.startswith('/') :
        errstr = "Internal Error"
        # "Internal Error : filename not full path : {0}\n".format(fpath)
        raise RuntimeError(errstr)

    try :
        dat = isy.soapcomm("GetSysConf", name=fpath)
    except IsySoapError, se :
        if fpath.startswith('/WEB/CONF/') :
            return
        raise
    else :
        if verbose :
            print "{0:<5} : {1}".format(len(dat), fpath)
        zf.writestr(fpath, dat)


def add_dir(isy, zf, fpath) :
    global verbose

    if not fpath.startswith('/') :
        raise RuntimeError(
            "Internal Error : dir name not full path : {0}".format(fpath))
    if not fpath.endswith('/') :
        fpath = fpath + '/'
    if verbose :
        print "{0:<5} : {1}".format("dir", fpath)
    zfi = zipfile.ZipInfo(fpath)
    zfi.external_attr = 16
    zf.writestr(zfi, '')

if __name__ == '__main__' :
    myisy = ISY.Isy(parsearg=1)
    zipit(myisy)
    exit(0)
