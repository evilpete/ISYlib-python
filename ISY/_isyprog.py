"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

# author : Peter Shipley <peter.shipley@gmail.com>
# copyrigh :  Copyright (C) 2013 Peter Shipley
# license : BSD

from ISY.IsyExceptionClass import IsyInvalidCmdError, IsyResponseError
from ISY.IsyProgramClass import IsyProgram
import xml.etree.ElementTree as ET
from warnings import warn


##
## ISY Programs Code
##
def load_prog(self, progid=None):
    """ Load Program status and Info

        args : none

        internal function call

    """
    if self.debug & 0x01 :
        print("load_prog")

    if not hasattr(self, '_progdict') or not isinstance(self._progdict, dict):
        self._progdict = dict ()

    if not hasattr(self, '_name2id') or not isinstance(self._name2id, dict):
        self._name2id = dict ()

    if progid  :
        xurl = "/rest/programs/" + progid
    else :
        xurl = "/rest/programs?subfolders=true"
        self.name2prog = dict ()

    prog_tree = self._getXMLetree(xurl, noquote=1)

    for pg in prog_tree.iter("program") :
        pdict = dict ()
        for k, v in pg.items() :
            pdict[k] = v
        for pe in list(pg):
            pdict[pe.tag] = pe.text

        # spacial case for root program node folder
        if not "parentId" in pdict :
            pdict["parentId"] = pdict["id"]

        if "id" in pdict :
            if str(pdict["id"]) in self._progdict :
                self._progdict[str(pdict["id"])].update(pdict)
            else :
                self._progdict[str(pdict["id"])] = pdict
            n = pdict["name"].upper()

#           # name2id to replace name2prog as a global lookup table
#           # but not sure if consolidating namespace between prog & nodes
#           # is it a good idea
#           if n in self._name2id :
#               # print("Dup name2id : \"" + n + "\" ", pdict["id"])
#               # print("name2id ", self._name2id[n])
#               pass
#           else :
#               self._name2id[n] = ("program", pdict["id"])

            if n in self.name2prog :
                print("Dup name : \"" + n + "\" ", pdict["id"])
                print("name2prog ", self.name2prog[n])
            else :
                self.name2prog[n] = pdict["id"]

    #self._printdict(self._progdict)
    #self._printdict(self.name2prog)



def get_prog(self, pname) :
    """ Get a Program object for given program name or ID

        args:
            pname : program name of id

        return:
            An IsyProgram class object representing the requested program

    """
    if self.debug & 0x01 :
        print("get_prog :" + pname)
    if not self._progdict :
        self.load_prog()

    progid = self._prog_get_id(pname)
    # print("\tprogid : " + progid)
    if progid in self._progdict :
        if not progid in self.progCdict :
            # print("not progid in self.progCdict:")
            # self._printdict(self._progdict[progid])
            self.progCdict[progid] = IsyProgram(self, self._progdict[progid])
        #self._printdict(self._progdict)
        # print("return : ",)
        #self._printdict(self.progCdict[progid])
        return self.progCdict[progid]
    else :
        if self.debug & 0x01 :
            print("Isy get_prog no prog : \"%s\"" % progid)
        raise LookupError("no prog : " + str(progid) )

def _prog_get_id(self, pname):
    """ Lookup prog value by name or ID
    returns ISY Id  or None
    """
    if isinstance(pname, IsyProgram) :
         return pname["id"]
    if isinstance(pname, (int, long)) :
	p = "{0:04X}".format(pname)
    else :
        p = str(pname).strip()

    if p.upper() in self._progdict :
        # print("_prog_get_id : " + p + " progdict " + p.upper())
        return p.upper()
    if p in self.name2prog :
        # print("_prog_get_id : " + p + " name2prog " + self.name2prog[p])
        return self.name2prog[p]

    # print("_prog_get_id : " + n + " None")
    return None

def prog_get_path(self, pname) :
    " get path of parent names "
    if not self._progdict :
        self.load_prog()
    prog_id = self._prog_get_id(pname)
    if prog_id is None :
        raise IsyValueError("prog_get_path: unknown program id : " + str(pname) )
    return self._prog_get_path(prog_id)

def _prog_get_path(self, prog_id) :
    fpath = self._progdict[prog_id]['name']
    pgm = self._progdict[ self._progdict[prog_id]['parentId'] ]

    while pgm['id'] != '0001' :
        fpath = pgm['name'] + "/" + fpath
        pgm = self._progdict[ pgm['parentId'] ]

    fpath = "/" + fpath
    return fpath

def prog_addrs(self) :
    """
        access method for prog address list
    """
    if not self._progdict :
        self.load_prog()
    return self._progdict.viewkeys()

def prog_get_src(self, pname):

    if not self._progdict :
        self.load_prog()

    prog_id = self._prog_get_id(pname)

    if prog_id is None :
        raise IsyValueError("prog_get_src: unknown program : " + str(prog_id) )

    r = self.soapcomm("GetSysConf", name="/CONF/D2D/" + prog_id + ".PGM")

    return r


def prog_iter(self):
    """ Iterate though program objects

        Returns an iterator over Program Objects types
    """
    if not self._progdict :
        self.load_prog()

    k = sorted(self._progdict.keys())
    for v in k :
        yield self.get_prog(v)

prog_valid_comm = ['run', 'runThen', 'runElse',
                'stop', 'enable', 'disable',
                'enableRunAtStartup', 'disableRunAtStartup']

def prog_cmd_list(self) :
    """ get list of valid commands for prog_comm() """
    return prog_valid_comm[:]

def prog_comm(self, paddr, cmd) :
    """ Send program command

        args:
            paddr = program name, address or program obj
            cmd = name of command

        raise:
            LookupError :  if node name or Id is invalid
            IsyPropertyError :  if property invalid
            TypeError :  if property valid

        Valid Commands : 'run', 'runThen', 'runElse', 'stop', 'enable', 'disable', 'enableRunAtStartup', 'disableRunAtStartup'

    calls  /rest/programs/<pgm-id>/<pgm-cmd>
    """

    prog_id = self._prog_get_id(paddr)

    #print("self.controls :", self.controls)
    #print("self.name2control :", self.name2control)

    if not prog_id :
        raise IsyValueError("prog_comm: unknown program id : " +
            str(paddr) )

    if not cmd in prog_valid_comm :
        raise IsyInvalidCmdError("prog_comm: unknown command : " +
            str(cmd) )

    self._prog_comm(prog_id, cmd)

def _prog_comm(self, prog_id, cmd) :
    """ called by prog_comm() after argument validation """
    # /rest/programs/<pgm-id>/<pgm-cmd>
    xurl = "/rest/programs/" + prog_id + "/" + cmd

    if self.debug & 0x02 :
        print("xurl = " + xurl)

    resp = self._getXMLetree(xurl)
    #self._printXML(resp)
    if resp.attrib["succeeded"] != 'true' :
        raise IsyResponseError("ISY command error : prog_id=" +
            str(prog_id) + " cmd=" + str(cmd))


def prog_rename(self, prog=None, progname=None ) :
    """
            Named args:
                prog            a prog id
                progname        New prog name
    """

    if prog is None :
        raise IsyValueError("prog_rename: program id is None")

    prog_id = self._prog_get_id(paddr)

    if prog_id is None :
        raise IsyValueError("prog_rename: unknown program id : " + str(prog) )

    if not isinstance(progname, str) :
        raise IsyValueError("new program name should be string")

    r = self._prog_rename(progid=prog_id, progname=progname )

    if self._progdict is not None and progid in self._progdict :
        self._progdict[progid]['name'] = progname
	self.name2prog[progname] = progid

    return r

def _prog_rename(self, progid=None, progname=None ) :
    """
            Named args:
                progid          a prog id
                progname        New prog name
    """

    if not isinstance(progid, str) :
        raise IsyValueError("program Id should be string")

    prog_path="/CONF/D2D/{0}.PGM".format(progid)

    result = self.soapcomm("GetSysConf", name=prog_path)

#    with open("prog-orig.xml", 'w') as fi:
#        fi.write(result)

    if result is None  :
        raise IsyResponseError("Error loading Sys Conf file {0}".format(prog_path))

    var_et = ET.fromstring(result)

    p = var_et.find("trigger/name")
    if not p is None:
        p.text = progname
    else :
        errorstr = "Internal Error, \"name\" element missing from D2D code :\n{0}\n".format(result)
        raise IsyRuntimeWarning(errorstr)

    # use method='html' to generate expanded empty elements
    new_prog_data = ET.tostring(var_et, method='html')

#    with open("prog-changed.xml", 'w') as fi:
#        fi.write(new_prog_data)
 

    r = self._sendfile(data=new_prog_data, filename=prog_path, load="y")

    return r


# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
