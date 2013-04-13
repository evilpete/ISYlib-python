from ISY.IsyExceptionClass import IsyResponseError

##
## WOL (Wake on LAN) funtions
##
def load_wol(self) :
    """ Load Wake On LAN IDs 

	args : none

	internal function call

    """
    if self.debug & 0x01 :
	print("load_wol called")
    wol_tree = self._getXMLetree("/rest/networking/wol")
    if wol_tree == None :
	if ( len(self.error_str) ) :
	    raise IsyResponseError (self.error_str)
	else:
	    raise IsyResponseError ("/rest/networking/wol")
    self.wolinfo = dict ()
    self.name2wol = dict ()
    for wl in wol_tree.iter("NetRule") :
	wdict = dict ()
	for k, v in wl.items() :
	    wdict[k] = v
	for we in list(wl):
	    wdict[we.tag] = we.text
	if "id" in wdict :
	    self.wolinfo[str(wdict["id"])] = wdict
	    self.name2wol[wdict["name"].upper()] = wdict["id"]
    self._printdict(self.wolinfo)
    #self._printdict(self.name2wol)
    self._writedict(self.wolinfo, "wolinfo.txt")

def wol(self, wid) :
    """
	Send Wake On LAN to registared wol ID
    """

    wol_id = self._wol_get_id(wid)

    # wol_id = str(wid).upper()

    if wol_id == None :
	raise IsyValueError("bad wol ID : " + wid)

    xurl = "/rest/networking/wol/" + wol_id

    if self.debug & 0x02 :
	print("wol : xurl = " + xurl)
    resp = self._getXMLetree(xurl)
    self._printXML(resp)
    if resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError("ISY command error : cmd=wol wol_id=" \
	    + str(wol_id))


def _wol_get_id(self, name) :
    """ wol name to wol ID """
    try:
	self.wolinfo
    except AttributeError:
	self.load_wol()
    name = str(name).upper()
    if name in self.wolinfo :
	return name

    if name in self.name2wol :
	return self.name2wol[name]

    return None


def wol_names(self) :
    """
    method to retrieve a list of WOL names
    returns List of WOL names and IDs or None
    """
    try:
	self.wolinfo
    except AttributeError:
	self.load_wol()
    return self.name2wol.keys()


def wol_iter():
    """ Iterate though Wol Ids values """
    try:
	self.wolinfo
    except AttributeError:
	self.load_wol()
    k = self.wolinfo.keys()
    for p in k :
	yield p


# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
