from ISY.IsyUtilClass import et2d
from ISY.IsyExceptionClass import IsyResponseError, IsyValueError

"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

##
## networking resources
##
def _load_networking(self, resource_id):
    if self.debug & 0x01 :
	print("load_wol called")
    xurl = "/rest/networking/{!s}".format(resource_id)
    if self.debug & 0x02 :
	print("_load_networking : xurl = " + xurl)
    net_res_tree = self._getXMLetree(xurl)
    if net_res_tree == None :
	if ( len(self.error_str) ) :
	    raise IsyResponseError (self.error_str)
	else:
	    raise IsyResponseError (xurl)
    net_dict = dict ()
    name2id = dict ()
    for netr in net_res_tree.iter('NetRule'):
	netrule = et2d(netr)
	if 'id' in netrule :
	    net_dict[netrule['id']] = netrule
	    if 'name' in netrule :
		name2id[netrule['name']] = netrule['id']
    return(net_dict, name2id)

def load_net_resource(self):
    """ Load node WOL and  Net Resource config infomation

	args: none
    """
    (self.net_resource, self.name2net_res) = self._load_networking("resources")
    #self._printdict(self.net_resource)
    #self._printdict(self.name2net_res)


def _net_resource_get_id(self, name):
    if not self.net_resource :
	self.load_net_resource()

    if name in self.net_resource:
	return name
    if name in self.name2net_res :
	return self.name2net_res[name]

    return None

def net_resource_run(self, rrid):
    """ Calls and executes net resource

	args:
	    rrid : network resource ID
    calls : /rest/networking/resources/<rrid>
    """

    rid = self._net_resource_get_id(rrid)

    if rid == None :
	raise IsyValueError("bad network resources ID : " + rrid)

    xurl = "/rest/networking/resources/{!s}".format(rid)

    if self.debug & 0x02 :
	print("wol : xurl = " + xurl)
    resp = self._getXMLetree(xurl)
    # self._printXML(resp)
    if None or  resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError("ISY network resources error : rid=" + str(rid))



def net_resource_names(self):
    """
    method to retrieve a list of networking resource names

	args: none

	returns List of names or None
    """
    if not self.net_resource :
	self.load_net_resource()

    return self.name2net_res.keys()

    
def net_resource_iter(self):
    """ iterate net_resource data

	args: none
    """ 
    if not self.net_resource :
	self.load_net_resource()
    for k, v in self.net_resource.items() :
	yield v



##
## WOL (Wake on LAN) funtions
##
def load_net_wol(self) :
    """ Load Wake On LAN networking resources 

	internal function call
    """
    (self.wolinfo, self.name2wol) = self._load_networking("wol")



def net_wol(self, wid) :
    """ Send Wake On LAN to registared wol ID

	args:
	    wid : WOL resource ID
    calls : /rest/networking/wol/<wol_id>
    """

    wol_id = self._net_wol_get_id(wid)

    # wol_id = str(wid).upper()

    if wol_id == None :
	raise IsyValueError("bad wol ID : " + wid)

    xurl = "/rest/networking/wol/" + wol_id

    if self.debug & 0x02 :
	print("wol : xurl = " + xurl)
    resp = self._getXMLetree(xurl)
    # self._printXML(resp)
    if resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError("ISY command error : cmd=wol wol_id=" \
	    + str(wol_id))


def _net_wol_get_id(self, name) :
    """ wol name to wol ID """
    if not self.wolinfo :
	self.load_wol()

    # name = str(name).upper()
    if name in self.wolinfo :
	return name

    if name in self.name2wol :
	return self.name2wol[name]

    return None


def net_wol_names(self) :
    """ method to retrieve a list of WOL names

	args: none

    returns List of WOL names and IDs or None
    """
    if not self.wolinfo :
	self.load_wol()
    return self.name2wol.keys()


def net_wol_iter(self):
    """ Iterate though Wol Ids values

	args: none
    """
    if not self.wolinfo :
	self.load_wol()

    for k, v in self.wolinfo.items() :
	yield v



# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
