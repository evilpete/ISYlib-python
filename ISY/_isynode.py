from ISY.IsyNodeClass import IsyNode, IsyScene #, IsyNodeFolder, _IsyNodeBase
from ISY.IsyUtilClass import IsySubClass
from ISY.IsyExceptionClass import IsyPropertyError, IsyResponseError
import warnings
# import string

"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

##
## Node funtions
##
def load_nodes(self) :
    """ Load node list scene list and folder info

	args : none

	internal function call

    """
    if not hasattr(self, '_nodedict') or not isinstance(self._nodedict, dict):
	 self._nodedict = dict ()

    if not hasattr(self, '_nodegroups') or not isinstance(self._nodegroups, dict):
	self._nodegroups  = dict ()

    if not hasattr(self, 'folderlist') or not isinstance(self._folderlist, dict):
	self._folderlist  = dict ()

    # self.nodeCdict = dict ()
    # self.node2addr = dict ()
    if self.debug & 0x01 :
	print("load_nodes pre _getXML")
    nodeinfo = self._getXMLetree("/rest/nodes")
    self._gen_nodedict(nodeinfo)
    self._gen_folder_list(nodeinfo)
    self._gen_nodegroups(nodeinfo)
    # self._printdict(self._nodedict)
    # print("load_nodes self.node2addr : ", len(self.node2addr))
    self._gen_member_list()

def _gen_member_list(self) :
    """ganerates node connecton lists

	internal function call

    """
    if not self._nodedict :
	return
    else :

	# Folders can only belong to Folders
	for faddr in self._folderlist :
	    # make code easier to read
	    foldr = self._folderlist[faddr]
	    # add members list if needed
	    if 'members' not in foldr :
		foldr['members'] = list()
	    # check if folder obj has a parent
	    if 'parent' in foldr :
		# this should always be true
		if foldr['parent-type'] == '3' and \
			foldr['parent'] in self._folderlist :
		    if 'members' not in self._folderlist[foldr['parent']] :
			self._folderlist[foldr['parent']]['members'] = list()
		    self._folderlist[foldr['parent']]['members'].append( foldr['address'])  
		else:
		    print("warn bad parenting foldr =", foldr)
		    warnings.warn("Bad Parent : Folder  (0)  (1) : (2)".format( \
			    foldr["name"], faddr, foldr['parent']), RuntimeWarning)

	# Scenes can only belong to Folders
	for sa in self._nodegroups :
	    s = self._nodegroups[sa]
	    if "parent" in s :
		if s['parent-type'] == '3' and  s['parent'] in self._folderlist :
		    self._folderlist[s['parent']]['members'].append( s['address'])
		else:
		    print("warn bad parenting s = ", s)
		    warnings.warn("Bad Parent : Scene  (0)  (1) : (2)".format( \
			    s["name"], sa, s['parent']), RuntimeWarning)

	# A Node can belong only to ONE and only ONE Folder or another Node
	for naddr in self._nodedict :
	    n = self._nodedict[naddr]
	    # print("n = ", n)
	    if 'pnode' in n and n['pnode'] != n['address'] :
		if 'members' not in self._nodedict[n['pnode']] :
		    self._nodedict[n['pnode']]['members'] = list ()
		self._nodedict[n['pnode']]['members'].append( n['address'] )

	    if 'parent' in n :
		if 'pnode' not in n or n['parent'] != n['pnode'] :
		    if n['parent-type'] == 3 :
			if n['parent'] in self._folderlist :
			    self._folderlist[n['parent']]['members'].append( n['address'])
		    elif  n['parent-type'] == 1 :
			if n['parent'] in self._nodegroups :
			    self._nodegroups[n['parent']]['members'].add( n['address'])
	    # 'parent': '16 6C D2 1', 'parent-type': '1',
	    # 'parent': '12743', 'parent-type': '3',
	    # if n.pnode == n.parent and n.pnode == n.address
		next



def _gen_folder_list(self, nodeinfo) :
    """ generate folder dictionary for load_node() """
    # self._folderlist = dict ()
    self.folder2addr = dict ()
    for fold in nodeinfo.iter('folder'):

	xelm = fold.find('address')
	if hasattr(xelm, 'text') :
	    if xelm.text in self._nodegroups :
		fprop = self._folderlist[xelm.text]
	    else :
		fprop = self._folderlist[xelm.text] = dict()
	else :
	    warnings.warn("Error : no address in folder", RuntimeWarning)
	    continue


	for k, v in fold.items() :
	    fprop[fold.tag + "-" + k] = v
	for child in list(fold):
	    fprop[child.tag] = child.text
	    if child.attrib :
		for k, v in child.items() :
		    fprop[child.tag + "-" + k] =  v
	# self._folderlist[fprop["address"]] = fprop
	self.folder2addr[fprop["name"]] = fprop["address"]
    #self._printdict(self._folderlist)
    #self._printdict(self.folder2addr)

def _gen_nodegroups(self, nodeinfo) :
    """ generate scene / group dictionary for load_node() """
    # self._nodegroups = dict ()
    self.groups2addr = dict ()
    for grp in nodeinfo.iter('group'):

	xelm = grp.find('address')
	if hasattr(xelm, 'text') :
	    if xelm.text in self._nodegroups :
		gprop = self._nodegroups[xelm.text]
	    else :
		gprop = self._nodegroups[xelm.text] = dict()
	else :
	    warnings.warn("Error : no address in scene", RuntimeWarning)
	    continue


	for k, v in grp.items() :
	    gprop[grp.tag + "-" + k] = v
	for child in list(grp) :
	    if child.tag == "parent" :
		gprop[child.tag] = child.text
		for k, v in child.items() :
		    gprop[child.tag + "-" + k] =  v
	    elif child.tag == "members" :
		glist = dict ()
		for lnk in child.iter('link'):
		    glist[lnk.text] = lnk.attrib['type']
		gprop[child.tag] = glist
	    else :
		gprop[child.tag] = child.text
		if child.attrib :
		    for k, v in child.items() :
			gprop[child.tag + "-" + k] =  v

	if "address" in gprop :
	    # self._nodegroups[gprop["address"]] = gprop
	    if "name" in gprop :
		if gprop["name"] in self.groups2addr :
		    warnings.warn("Duplicate group name (0) : (1) (2)".format(gprop["name"], \
			    str(gprop["address"]), self.groups2addr[gprop["name"]]), RuntimeWarning)
		else :
		    self.groups2addr[gprop["name"]] = str(gprop["address"])
	else :
	    # should raise an exception ?
	    self._printinfo(grp, "Error : no address in group :")


def _gen_nodedict(self, nodeinfo) :
    """ generate node dictionary for load_node() """
    self.node2addr = dict()
    for inode in nodeinfo.iter('node'):
	# self._printinfo(inode, "\n\n inode")

	xelm = inode.find('address')
	if hasattr(xelm, 'text') :
	    if xelm.text in self._nodedict :
		idict = self._nodedict[xelm.text]
	    else :
		idict = self._nodedict[xelm.text] = dict()
	else :
	    warnings.warn("Error : no address in node", RuntimeWarning)
	    continue


	for k, v in inode.items() :
	    idict[inode.tag + "-" + k] = v
	for child in list(inode) :
	    # self._printinfo(child, "\tchild")

	    if child.tag == "parent" :
		idict[child.tag] = child.text
		for k, v in child.items() :
		    idict[child.tag + "-" + k] = v
	    # special case where ST, OL, and RR
	    elif child.tag == "property" :
		if child.tag not in idict :
		    idict[child.tag] = dict ()
		nprop = dict ()
		for k, v in child.items() :
		    # print("child.items", k, v)
		    nprop[k] = v
		if "id" in nprop :
		    idict[child.tag][nprop["id"]] = nprop
	    else :
		idict[child.tag] = child.text

	if "address" in idict :
	    # self._nodedict[idict["address"]] = idict
	    if "name" in idict :
		if idict["name"] in self.node2addr :
		    warn_mess = "Duplicate Node name (0) : (1) (2)".format(idict["name"], \
			    idict["address"], self.node2addr[idict["name"]])
		    warnings.warn(warn_mess, RuntimeWarning)
		else :
		    self.node2addr[idict["name"]] = idict["address"]

	else :
	    # should raise an exception
	    # self._printinfo(inode, "Error : no address in node :")
	    warnings.warn("Error : no address in node", RuntimeWarning)
    #print("\n>>>>\t", self._nodedict, "\n<<<<<\n")



#
# access methods to Node data
#
def node_names(self) :
    """  access method for node names
	returns a dict of ( Node names : Node address )
    """
    if not self.node2addr :
	self.load_nodes()
    return self.node2addr[:]

def scene_names(self) :
    """ access method for scene names
	returns a dict of ( Node names : Node address )
    """
    if not self.groups2addr :
	self.load_nodes()
    return self.groups2addr[:]

def node_addrs(self) :
    """ access method for node addresses
	returns a iist scene/group addresses
    """
    if not self._nodedict :
	self.load_nodes()
    return self._nodedict.viewkeys()

def scene_addrs(self) :
    """ access method for scene addresses
	returns a iist scene/group addresses
    """
    if not self._nodegroups :
	self.load_nodes()
    return self._nodegroups.viewkeys()


def get_node(self, node_id) :
    """ Get a Node object for given node or scene name or ID

	args:
	    node : node name of id

	return:
	    An IsyNode object representing the requested Scene or Node

    """
    if self.debug & 0x01 :
	print("get_node")

    nodeid = self._node_get_id(node_id)

    if nodeid in self.nodeCdict :
	return self.nodeCdict[nodeid]

    if nodeid in self._nodedict :
	self.nodeCdict[nodeid] = IsyNode(self, self._nodedict[nodeid])
	return self.nodeCdict[nodeid]

    elif nodeid in self._nodegroups:
	self.nodeCdict[nodeid] = IsyScene(self, self._nodegroups[nodeid])
	return self.nodeCdict[nodeid]

    elif nodeid in self._folderdict:
	self.nodeCdict[nodeid] = IsyFolder(self, self._folderdict[nodeid])
	return self.nodeCdict[nodeid]

    else :
	print("Isy get_node no node : \"{!s:}\"".format(nodeid))
	raise LookupError("no node such Node : " + str(nodeid) )


def _node_get_id(self, nid):
    """ node/scene/Folder name to node/scene/folder ID """

    if not self._nodedict :
	self.load_nodes()

    if isinstance(nid, IsySubClass) :
	 return nid["addr"]
    else :
	n = str(nid).strip()

    ##

    if n in self._nodedict :
	# print("_node_get_id : " + n + " nodedict " + n
	return n

    if n in self.node2addr :
	# print("_node_get_id : " + n + " node2addr " + self.node2addr[n])
	return self.node2addr[n]

    ##

    if n in self._nodegroups :
	# print("_node_get_id : " + n + " nodegroups " + n)
	return n

    if n in self.groups2addr :
	# print("_node_get_id : " + n + " groups2addr " + self.groups2addr[n])
	return self.groups2addr[n]

    ##

    if n in self.folder2addr :
	# print("_node_get_id : " + n + " folder2addr " + self.folder2addr[n])
	return self.folder2addr[n]

    if n in self._folderdict :
	# print("_node_get_id : " + n + " folderdict " + n)
	return n


	# Fail #
    #print("_node_get_id : " + n + " None")
    return None



# [Needs fixing]
#
# Get property for a node
#
def node_get_prop(self, naddr, prop_id) :
    """ Get node property 
        args:
	    naddr = name, address or node obj
            prop_id = name of property
 
        raise:
            LookupError :  if node name or Id is invalid
            IsyPropertyError :  if property invalid
    """

    #<isQueryAble>true</isQueryAble>
    if self.debug & 0x01 :
	print("node_get_prop")

    node_id = self._node_get_id(naddr)
    if not node_id :
	raise LookupError("node_get_prop: unknown node : " + str(naddr) )

    if prop_id :
	prop = prop_id
	if "isQueryAble" in self.controls[prop_id] and \
		self.controls["prop_id"]["isQueryAble"] == "false" :
	    raise IsyPropertyError("non Queryable property " + prop_id)

    if prop_id in ['ST', 'OL', 'RR'] :
	if prop in self._nodedict[node_id]["property"] :
	    return self._nodedict[node_id]["property"]["value"]
	else :
	    raise IsyPropertyError("unknown property " + prop_id)
	
    if prop in self._nodedict[node_id] :
	return self._nodedict[node_id][prop]
    else :
	raise IsyPropertyError("unknown property " + prop_id)
    pass

# Set property for a node
#
def node_set_prop(self, naddr, prop, val) :
    """ Set node property 
        args:
	    naddr = name, address or node obj
            prop = name of property
	    val = new value to assign 
 
        raise:
            LookupError :  if node name or Id is invalid
            IsyPropertyError :  if property invalid
            TypeError :  if property valid

    calls /rest/nodes/<node-id>/set/<property>/<value>
    """
    if self.debug & 0x01 :
	print("node_set_prop")

    node_id = self._node_get_id(naddr)
    if not node_id :
	raise LookupError("node_set_prop: unknown node : " + str(naddr) )

    prop_id = self._get_control_id(prop);
    if prop_id :
	# raise TypeError("node_set_prop: unknown prop : " + str(cmd) )
	if "readOnly" in self.controls[prop_id] and \
		self.controls["prop_id"]["readOnly"] == "true" :
	    raise IsyPropertyError("readOnly property " + prop_id)

    prop = str(prop)

    if "isNumeric" in self.controls[prop_id] and \
	    self.controls["prop_id"]["isNumeric"] == "true" and \
	    not str(val).isdigit :
	raise IsyPropertyError("Numeric property " + prop_id)

#        if not prop in ['ST', 'OL', 'RR'] :
#            raise TypeError("node_set_prop: unknown propery : " + str(prop) )

    # if val :
    #       pass
    # self._node_set_prop(naddr, prop, val)
    self._node_send(naddr, "set", prop, val)
    if not self.eventupdates :
	self._updatenode(naddr)

# to  replace _node_set_prop and _node_comm
def _node_send(self, naddr, action,  prop, *args) :
    """ called by node_comm() or  node_set_prop() after argument validation """
    #print("_node_send : node=%s prop=%s val=%s" % str(naddr), prop, val)
    # print ("_node_send : node=" + str(naddr) + " prop=" + prop + " val=" + val )
    xurl = "/rest/nodes/{!s:}/{!s:}/{!s:}/{!s:}".format(naddr, action, prop, "/".join(str(x) for x in args) )
    if self.debug & 0x02 : print("xurl = " + xurl)
    resp = self._getXMLetree(xurl)
    self._printXML(resp)
    if resp == None or resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError(
		"Node Cmd/Property Set error : node=%s prop=%s " %
		naddr, prop )

#def _node_set_prop(self, naddr, prop, val) :
#    """ node_set_prop without argument validation """
#    #print("_node_set_prop : node=%s prop=%s val=%s" % str(naddr), prop, val)
#    print ("_node_set_prop : node=" + str(naddr) + " prop=" + prop +
#		" val=" + val )
#    xurl = "/rest/nodes/" + naddr + "/set/" + prop + "/" + val
#    resp = self._getXMLetree(xurl)
#    self._printXML(resp)
#    if resp.attrib["succeeded"] != 'true' :
#	raise IsyResponseError("Node Property Set error : node=%s prop=%s val=%s" %
#		naddr, prop, val )
#

#
# Send command to Node/Scene
#
def node_comm(self, naddr, cmd, *args) :
    """ Send node command 

        args:
	    naddr = name, address or node obj
            cmd = name of command
	    value = optional value argument for cmd
	    
        raise:
            LookupError :  if node name or Id is invalid
            IsyPropertyError :  if property invalid
            TypeError :  if property valid

    calls /rest/nodes/<node-id>/cmd/<cmd>>/<cmd value>
    """
    if self.debug & 0x04 :
	print("node_comm", naddr, cmd)
    node_id = self._node_get_id(naddr)
    cmd_id = self._get_control_id(cmd)

    #print("self.controls :", self.controls)
    #print("self.name2control :", self.name2control)

    if not node_id :
	raise LookupError("node_comm: unknown node : " + str(naddr) )
    print("naddr : ", naddr, " : ", node_id)

    if not cmd_id :
	raise TypeError("node_comm: unknown command : " + str(cmd) )

    #self._node_comm(node_id, cmd_id, args)
    self._node_send(node_id, "cmd", cmd_id, args)
    if not self.eventupdates :
	self._updatenode(naddr)

#
# Send command to Node without all the arg checking
#
#def _node_comm(self, node_id, cmd_id, *args) :
#    """ send command to a node or scene without name to ID overhead """
#    if self.debug & 0x04 :
#	print("_node_comm", node_id, cmd_id)
#    # rest/nodes/<nodeid>/cmd/<command_name>/<param1>/<param2>/.../<param5>
#    xurl = ("/rest/nodes/" + node_id + "/cmd/" + cmd_id +
#	"/" + "/".join(str(x) for x in args) )
#
#    if self.debug & 0x02 :
#	    print("xurl = " + xurl)
#    resp = self._getXMLetree(xurl)
#    self._printXML(resp)
#    if resp.attrib["succeeded"] != 'true' :
#	raise IsyResponseError("ISY command error : node_id=" +
#	    str(node_id) + " cmd=" + str(cmd_id))
#




##
##  Node Type
##
def load_node_types(self) :
    """ Load node type info into a multi dimentional dictionary

	args : none

	internal function call

    """
    if self.debug & 0x01 :
	print("load_node_types called")
    typeinfo = self._getXMLetree("/WEB/cat.xml")
    if not hasattr(self, 'nodeCategory') or not isinstance(self.nodeCategory, dict):
	self.nodeCategory = dict ()
    for ncat in typeinfo.iter('nodeCategory'):
	if not ncat.attrib["id"] in self.nodeCategory :
	    self.nodeCategory[ncat.attrib["id"]] = dict ()
	self.nodeCategory[ncat.attrib["id"]]["name"] = ncat.attrib["name"]
    typeinfo = self._getXMLetree("/WEB/1_fam.xml")
    for ncat in typeinfo.iter('nodeCategory'):
	for subcat in ncat.iter('nodeSubCategory'):
	    ## FIX
	    if not ncat.attrib["id"] in self.nodeCategory :
		self.nodeCategory[ncat.attrib["id"]] = dict ()
	    # print("ID : ", ncat.attrib["id"], " : ", subcat.attrib["id"])
	    # print("ID  name: ", subcat.attrib["name"])
	    self.nodeCategory[ncat.attrib["id"]][subcat.attrib["id"]] = subcat.attrib["name"]
	    #self._printinfo(subcat, "subcat :")
    # print("nodeCategory : ", self.nodeCategory)
    # self._printdict(self.nodeCategory)

def node_get_type(self, typid) :
    """ Take a node's type value and returns a string idnentifying the device """
    if not self.nodeCategory :
	self.load_node_types()
    #
    # devcat = "UNKNOWN"
    # subcat = "UNKNOWN"
    #
    a = typid.split('.')
    #
    if len(a) >= 2 :
	devcat = a[0]
	subcat = a[1]
	if self.nodeCategory[a[0]] :
	    devcat = self.nodeCategory[a[0]]["name"]
	    if self.nodeCategory[a[0]][a[1]] :
		subcat = self.nodeCategory[a[0]][a[1]].replace('DEV_CAT_', '')
    else :
	devcat = typid
	subcat = ""
    #
    return (devcat, subcat)


def node_iter(self, nodetype=""):
    """ Iterate though nodes

	args: 
	    nodetype : type of node to return

	returns :
	    Return an iterator over the Node Obj
    """
    if not self._nodedict :
	self.load_nodes()
    if nodetype == "node" :
	k = self._nodedict.keys()
    elif nodetype == "scene" :
	k = self._nodegroups.keys()
    else :
	k = self._nodedict.keys()
	k.extend(self._nodegroups.keys())
    for n in k :
	yield self.get_node(n)


## redundant
#def _updatenode(self, naddr) :
#    """ update a node's property from ISY device """
#    xurl = "/rest/nodes/" + self._nodedict[naddr]["address"]
#    if self.debug & (0x01 & 0x10) :
#	print("_updatenode pre _getXML")
#    _nodestat = self._getXMLetree(xurl)
#    # del self._nodedict[naddr]["property"]["ST"]
#    for prop in _nodestat.iter('property'):
#	tprop = dict ( )
#	for k, v in prop.items() :
#	    tprop[k] = v
#	if "id" in tprop :
#	    self._nodedict[naddr]["property"][tprop["id"]] = tprop
#    self._nodedict[naddr]["property"]["time"] = time.gmtime()


# redundant
def _updatenode(self, naddr) :
    """ update a node's property from ISY device """
    xurl = "/rest/nodes/" + naddr
    if self.debug & 0x01 :
	print("_updatenode pre _getXML")
    _nodestat = self._getXMLetree(xurl)
    # del self._nodedict[naddr]["property"]["ST"]
    for child in list(_nodestat) :
	if child.tag == "property" : next
	if child.text :
	    self._nodedict[naddr][child.tag] = child.text
	if child.attrib :
	    for k, v in list(child.items()) :
		self._nodedict[naddr][child.tag + "-" + k] =  v

        for prop in _nodestat.iter('property'):
            tprop = dict ( )
            for k, v in prop.items() :
                tprop[k] = v
            if "id" in tprop :
                self._nodedict[naddr]["property"][tprop["id"]].update(tprop)

        self._nodedict[naddr]["property"]["time"] = time.gmtime()


#
# Send command to Node/Scene
#
def node_enable(self, naddr, enable=True) :
    """ enable/disable node

        args:
	    naddr = name, address or node obj
            enable = bool ( True=enable / False=disable)
	    
        raise:
            LookupError :  if node name or Id is invalid
            IsyResponseError :  if Error in ISY responce

    calls /rest/nodes/<node-id>/enable
    calls /rest/nodes/<node-id>/disable
    """
    if self.debug & 0x04 :
	print("node_enable", naddr, cmd)
    node_id = self._node_get_id(naddr)

    if not node_id :
	raise LookupError("node_comm: unknown node : " + str(naddr) )
    # print("naddr : ", naddr, " : ", node_id)

    if enable :
	op = "enable"
    else :
	op = "disable"

    xurl = "/rest/nodes/{!s:}/{!s:}".format(naddr, op) 
    if self.debug & 0x02 : print("xurl = " + xurl)
    resp = self._getXMLetree(xurl)
    self._printXML(resp)
    if resp == None or resp.attrib["succeeded"] != 'true' :
	raise IsyResponseError(
		"Node Cmd/Property Set error : node=%s prop=%s " %
		naddr, prop )

# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
