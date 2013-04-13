
from ISY.IsyExceptionClass import IsyInvalidCmdError, IsyResponseError
from ISY.IsyProgramClass import IsyProgram


##
## ISY Programs Code
##
def load_prog(self):
    """ Load Program status and Info

	args : none

	internal function call

    """
    if self.debug & 0x01 :
	print("load_prog called")
    prog_tree = self._getXMLetree("/rest/programs?subfolders=true", noquote=1)
    if not hasattr(self, '_progdict') or not isinstance(self._progdict, dict):
	self._progdict = dict ()
    self.name2prog = dict ()
    for pg in prog_tree.iter("program") :
	pdict = dict ()
	for k, v in pg.items() :
	    pdict[k] = v
	for pe in list(pg):
	    pdict[pe.tag] = pe.text
	if "id" in pdict :
	    if str(pdict["id"]) in self._progdict :
		self._progdict[str(pdict["id"])].update(pdict)
	    else :
		self._progdict[str(pdict["id"])] = pdict
	    n = pdict["name"].upper()
	    if n in self.name2prog :
		print("Dup name : \"" + n + "\" ", pdict["id"])
		print("name2prog ", self.name2prog[n])
	    else :
		self.name2prog[n] = pdict["id"]
    #self._printdict(self._progdict)
    #self._printdict(self.name2prog)



def get_prog(self, pname) :
    """ get prog class obj """
    if self.debug & 0x01 :
	print("get_prog :" + pname)
    try:
	self._progdict
    except AttributeError:
	self.load_prog()
#       except:
#           print("Unexpected error:", sys.exc_info()[0])
#           return None
    finally:
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


def prog_iter(self):
    """ Iterate though program objects

	Returns an iterator over Program Objects types
    """
    try:
	self._progdict
    except AttributeError:
	self.load_prog()
#       except:
#           print("Unexpected error:", sys.exc_info()[0])

    k = self._progdict.keys()
    for v in k :
	yield self.get_prog(v)

prog_valid_comm = ['run', 'runThen', 'runElse',
		'stop', 'enable', 'disable',
		'enableRunAtStartup', 'disableRunAtStartup']

def prog_cmd_list(self) :
    return prog_valid_comm[:]

def prog_comm(self, paddr, cmd) :
    prog_id = self._prog_get_id(paddr)

    #print("self.controls :", self.controls)
    #print("self.name2control :", self.name2control)

    if not prog_id :
	raise IsyInvalidCmdError("prog_comm: unknown node : " +
	    str(paddr) )

    if not cmd in prog_valid_comm :
	raise IsyInvalidCmdError("prog_comm: unknown command : " +
	    str(cmd) )

    self._prog_comm(prog_id, cmd)

def _prog_comm(self, prog_id, cmd) :
    """ send command to a program without name to ID overhead """
    # /rest/programs/<pgm-id>/<pgm-cmd>
    xurl = "/rest/programs/" + prog_id + "/" + cmd 

    if self.debug & 0x02 :
	print("xurl = " + xurl)

    resp = self._getXMLetree(xurl)
    self._printXML(resp)
    if resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError("ISY command error : prog_id=" +
	    str(prog_id) + " cmd=" + str(cmd))



# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
