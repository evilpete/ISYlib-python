#!/usr/bin/env python
"""
    generate backup for ISY
"""

__author__ = "Peter Shipley"


import os
import zipfile
# import pprint
import time
import tempfile
import argparse
import xml.etree.ElementTree as ET
import ISY
from ISY.IsyUtilClass import et2d
from ISY.IsyExceptionClass import IsySoapError

dirset = set()
fileset = set()
#folder = None
outfile = None
verbose = 0
restore = 0
noop = False
# noop = True

local_time = None

debug = 0

backup_flags   = 0b0000
backup_sysconf = 0b0001
backup_userweb = 0b0010
backup_ui      = 0b0100
backup_logs    = 0b1000
# backup_system  = 0b1000
backup_all = (backup_sysconf | backup_userweb | backup_ui )

# this makes the backup not usable for restores
# but is good for debuging since unzip will not
# extract file with absolute paths from root
zip_noroot = False

reboot_after = False


def date_time2str(dt):
    return "{0}-{1}-{2} {3}:{4}:{5}".format(*dt)

#ISY-Backup.v4.1.2__Fri 2014.03.14 17.46.52.zip
#uuid.00.21.b9.00.e7.08.zip*

def parse_args(isy):
#    global folder
    global noop
    global outfile
    global restore
    global verbose
    global backup_flags
    global reboot_after
    global zip_noroot


    parser = isy.parser

#    if "parser" in isy:
#       parser = isy.parser
#    else:
#       if debug:
#           print "new parser"
#       parser = argparse.ArgumentParser()


    parser.add_help = True
    parser.epilog = "Default is to back up system, userweb, and web UI configs"

    # dest="outfile",

    parser.add_argument("-A", "--backup-all", action='store_true',
                        help="backup all (sys config, User Web, UI config) ")

    parser.add_argument("-L", "--backup-logs", action='store_true',
                        help="backup system log files")

    parser.add_argument("-W", "--backup-userweb", action='store_true',
                        help="backup user web files")

    parser.add_argument("-C", "--backup-sysconf", action='store_true',
                        help="backup system config")

    parser.add_argument("-U", "--backup-ui", action='store_true',
                        help="backup web UI config")

    parser.add_argument("-n", "--noop", action='store_true',
                        help="noop test arg")

    parser.add_argument("-R", "--Reboot", action='store_true',
                        help="Reboot after restore")

    parser.add_argument("-r", "--restore", action='store_true',
                        help="restore backup")

    parser.add_argument("-h", "--help", action='help',
                        default=argparse.SUPPRESS)

    parser.add_argument("-f", "--file", dest="outfile",
                        help="backup file")

    parser.add_argument("-N", "--noroot", action='store_true',
                        help="backup without root origin")

#    parser.add_argument("-c", "--copy", dest="copy",
#                       help="copy config tree to folder")

    parser.add_argument('-v', '--verbose', action='count')

    args = parser.parse_args()
    # args, unknown_args = parser.parse_known_args()

#    if args.outfile and args.folder:
#       print "you can't use both file and folder"
#       parser.print_help()
#       exit(0)

    if args.restore and not args.outfile:
        parser.error('--file is required when --restore is set.')

    if args.Reboot: reboot_after = True

    if args.backup_sysconf: backup_flags |= backup_sysconf
    if args.backup_ui: backup_flags |= backup_ui
    if args.backup_userweb: backup_flags |= backup_userweb
    if args.backup_all: backup_flags |=  (backup_all | backup_logs)
    if args.backup_logs: backup_flags |= backup_logs
    if backup_flags == 0: backup_flags = backup_all

    if debug:
        print "backup_flags = {0:04b}".format(backup_flags)
    noop    = args.noop
    outfile = args.outfile
    verbose = args.verbose
    restore = args.restore
    zip_noroot = args.noroot
#    folder = args.folder



def restore_isy(isy):
    if outfile is None:
        raise argparse.ArgumentTypeError("no restore file given")

    # mybackupid = "uuid.{0}.zip".format(myisy.id.replace(':', '.'))

    zf = zipfile.ZipFile(outfile, "r")
    isybackup = zf.namelist()[0]
    # print isybackup

#    if verbose:
#       for f in zf.infolist():
#           print "{0:<30} : {1:6} : {2:#010x} ({3:#04o}) ".format(
#                   f.filename,
#                   f.file_size,
#                   f.external_attr,
#                   ( (f.external_attr >> 16L) & 0x0FFF)
#               )


    if not (isybackup.startswith("uuid") and isybackup.endswith(".zip")):
        raise SystemExit("Invalid backup\n")

    td = tempfile.mkdtemp()

    zf.extract(isybackup, td)
    zf.close()
    uuidfile = "{0}/{1}".format(td, isybackup)

    zff = zipfile.ZipFile(uuidfile, "r")
    zff_info = zff.infolist()

    if verbose:
        print "{0} files to be retored".format(len(zff_info))

    restore_filter = None
    if backup_flags != backup_all:
        restore_filter_list = list()

        if (backup_flags & backup_sysconf):
            restore_filter_list.append("/CONF")

        if (backup_flags & backup_userweb):
            restore_filter_list.append("/USER/WEB/")

        if (backup_flags & backup_ui):
            restore_filter_list.append("/WEB/CONF/")

        if (backup_flags & backup_logs):
            restore_filter_list.append("/LOG/")

        restore_filter = tuple(restore_filter_list)

    for z in zff_info:
        if restore_filter and not z.filename.startswith(restore_filter):
            if vebose:
                print "skipping {0:<30} : Not in restore path".format(z.filename)
            continue

        if (z.external_attr & 0x0010) or z.filename.endswith("/"):
            if verbose:
                print "skipping {0:<30} : directory".format(z.filename)
            continue

        if verbose:
            print "{0:<30} : {1:6} : {2:#010x} ({3:04o}) {4}".format(
                    z.filename,
                    z.file_size,
                    z.external_attr,
                    ((z.external_attr >> 16L) & 0x0FFF),
                    date_time2str(z.date_time)
                )

        if (not z.filename.startswith("/")):
            if verbose:
                print "skipping {0:<30} : not full path".format(z.filename)
            continue

        if not noop:
            fdata = zff.read(z)
            try:
                r = isy._sendfile(data=fdata, filename=z.filename, load="y")
            except IsySoapError, se:
                if se.code() == 403:
                    print "Error restoring {0} : Forbidden (code=403)".format(z.filename)
                else:
                    raise

    zff.close()

    os.unlink(uuidfile)
    os.rmdir(td)

def backup_isy(isy):
    global outfile
    # global verbose
    time_str = time.strftime("%a_%Y.%m.%d_%H.%M.%S" , time.localtime())

    # if folder is None:
    if outfile is None:
        outfile = "ISY-Backup.v{0}_{1}.zip".format(isy.app_version, time_str)
    elif not outfile.endswith((".zip", ".ZIP")):
        outfile = outfile + ".zip"

    backupid = "uuid.{0}.zip".format(myisy.id.replace(':', '.'))


    if (backup_flags & backup_sysconf):
        zip_get_conf(isy)

    if (backup_flags & backup_userweb):
        zip_get_userweb(isy)

    if (backup_flags & backup_logs):
        zip_get_logfiles(isy)

    if (backup_flags & backup_ui):
        zip_get_ui_conf(isy)

    tf = tempfile.NamedTemporaryFile(delete=False)
    zf = zipfile.ZipFile(tf, "w")

    for d in sorted(dirset):
        add_dir(isy, zf, d)

    for f in sorted(fileset):
        add_file(isy, zf, f)

    zf.close()
    tf.close()

    zff = zipfile.ZipFile(outfile, "w")
    zff.create_system = os.uname()[0]

    zff.write(tf.name, backupid)
    zff.close()
    os.unlink(tf.name)
    if verbose:
        print "Backup completed"
        print "output file = ", outfile


def zip_get_ui_conf(isy):
    dirset.add("/WEB/CONF")
    fileset.add("/WEB/CONF/CAMS.JSN")

def zip_get_logfiles(isy):
    dirset.add("/LOG/")
    fileset.add("/LOG/A.LOG")
    fileset.add("/LOG/ERRORA.LOG")
    fileset.add("/LOG/UPRICEA.LOG")
    fileset.add("/LOG/UMSGA.LOG")
    fileset.add("/LOG/UDRLCA.LOG")
    fileset.add("/LOG/UMETERA.LOG")


def zip_get_conf(isy):

    dat = isy.soapcomm("GetSysConfFiles")
    flist = et2d(ET.fromstring(dat))
    # pprint.pprint(flist)

    if "dir-name" in flist:
        if isinstance(flist['dir-name'], list):
            for d in flist['dir-name']:
                if d.startswith("/"):
                    dirset.add(d)
                else:
                    dirset.add("/CONF/" + d)
        else:
            if flist['dir-name'].startswith("/"):
                dirset.add(flist['dir-name'])
            else:
                dirset.add("/CONF/" + flist['dir-name'])

    if "entry" in flist:
        if isinstance(flist['entry'], list):
            for f in flist['entry']:
                fileset.add("/CONF/" + f)
        else:
            fileset.add("/CONF" + flist["entry"])


def zip_get_userweb(isy):

    dat = isy.soapcomm("GetUserDirectory")
    flist = et2d(ET.fromstring(dat))

    # pprint.pprint(flist)

    if "dir" in flist:
        if isinstance(flist['dir'], list):
            for d in flist['dir']:
                dirset.add(d["dir-name"])
        else:
            dirset.add(flist['dir']["dir-name"])

    if "dir" in flist:
        if isinstance(flist['dir'], list):
            for d in flist['dir']:
                dirset.add(d["dir-name"])
        else:
            dirset.add(flist['dir']["dir-name"])

    if "file" in flist:
        if isinstance(flist['file'], list):
            for f in flist['file']:
                fileset.add(f["file-name"])
        else:
            fileset.add(flist['file']["file-name"])


def add_file(isy, zf, fpath):
    # global verbose
    global local_time

    if not fpath.startswith('/'):
        errstr = "Internal Error"
        # "Internal Error : filename not full path : {0}\n".format(fpath)
        raise RuntimeError(errstr)

    try:
        dat = isy.soapcomm("GetSysConf", name=fpath)
    except IsySoapError, se:
        if fpath.startswith('/WEB/CONF/'):
            return
        raise
    else:
        if verbose:
            print "{0:<5} : {1}".format(len(dat), fpath)

        if (zip_noroot):
            fpath=fpath[1:]


        if local_time is None:
            local_time =  time.localtime()
        zfi = zipfile.ZipInfo(fpath)
        zfi.date_time = local_time[:6]
        zfi.compress_type = zipfile.ZIP_STORED
        zfi.external_attr = (0o0644 << 16L)
        zf.writestr(zfi, dat)


def add_dir(isy, zf, fpath):
    # global verbose

    if not fpath.startswith('/'):
        raise RuntimeError(
            "Internal Error : dir name not full path : {0}".format(fpath))
    if not fpath.endswith('/'):
        fpath = fpath + '/'
    if verbose:
        print "{0:<5} : {1}".format("dir", fpath)
    zfi = zipfile.ZipInfo(fpath)
    zfi.compress_type = zipfile.ZIP_STORED
    zfi.external_attr = (0o040755 < 16L) | 0x10
    zf.writestr(zfi, '')

if __name__ == '__main__':
    myisy = ISY.Isy(parsearg=1, faststart=1)
    parse_args(myisy)
    if restore:
        restore_isy(myisy)
        if reboot_after:
            myisy.reboot()
    else:
        backup_isy(myisy)
    exit(0)
