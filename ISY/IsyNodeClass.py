"""

Devices controlled my the ISY are represented as "nodes" on the ISY device and with Node Objects in the API

There are three types of Node Object:

    * IsyNode - Node Object 
	Represent lights, switches, motion sensors 
    * IsyScene - Scene Object
	Represents Scenes contains Nodes that comprise a "Scene"
    * IsyNodeFolder - Can hold Scene's or Nodes
	a organizational obj for Scene's and Nodes

Only IsyNode Objects maintain "state" 

    What states are maintined depend on the physical node device itself
    but they can include
	- on, off of dim level
	- temperature
	- wattage

    Nodes can have "members" or subnodes

IsyScene Objects can take commands but do not maintin a queryable state

    A Scene is predefined state for one or more nodes
    scenes can only be comprised of nodes which are call "members"

    only nodes can be members of a scene 

IsyNodeFolders are just for organizing  

    Nodes, Scenes and Folders can be members of a Folder 



"""

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"

from ISY.IsyUtilClass import IsySubClass, val2bool 
from ISY.IsyExceptionClass import *
# from IsyClass import *
# from IsyNodeClass import *
# from IsyProgramClass import *
# from IsyVarClass import *

__all__ = ['IsyNode', 'IsyNodeFolder', 'IsyScene']


# library_using_super

class _IsyNodeBase(IsySubClass):

    #_objtype = (0, "unknown")
    _objtype = "unknown"

    def on(self, val=255) :
        """ Send On command to a node

            args: 
                take optional value for on level

        """
	if not str(val).isdigit :       
	    raise IsyTypeError("On Command : Bad Value : node=%s val=%s" %
		    self._mydict["address"], str(val))

        self.isy._node_send(self._mydict["address"], "cmd", "DON", val)
        #if "property" in self._mydict :
        #    self._mydict["property"]["time"] = 0
        # self.update()

    def off(self) :
        """ Send Off command to a node

            args: None

        """
        self.isy._node_send(self._mydict["address"], "cmd", "DOF")
        if "property" in self._mydict :
            # self._mydict["property"]["time"] = 0
            if "ST" in  self._mydict["property"] :
                self._mydict["property"]["ST"]["value"] = 0
                self._mydict["property"]["ST"]["formatted"] = "Off"

    def beep(self) :
        self.isy._node_send(self._mydict["address"], "cmd", "BEEP")


    def get_path(self): 
	return self.isy._node_get_path(self._mydict['address'], self._objtype)
    path = property(get_path) 

    def members_list(self) :
	pass

    def member_iter(self, flag=0):
        return self.members_list()

    def member_list(self):
        if 'members' in self._mydict :
            # print("mydict['members'] : ", type(self._mydict['members']) )
            if type(self._mydict['members']) == 'dict' :
                return self._mydict['members'].keys()
            # if type(self._mydict['members']) == 'list' :
            return self._mydict['members'][:]
        return [ ]

    def is_dimable(self) :
	if 'type' in self._mydict :
	    a = self._mydict["type"].split('.') 
	    if a[0] == "1" :
		return True
	return False
    dimable = property(is_dimable)


    def get_callback(self) :
	return self.isy.callback_get(self._mydict["address"])
    def set_callback(self, func, *args) :
	if func == None :
	    return self.isy.callback_del(self._mydict["address"])
	else :
	    return self.isy.callback_set(self._mydict["address"], func, args)
    callback = property(get_callback, set_callback)


    def is_member(self, obj) :
        if "members" in self._mydict :
            if isinstance(obj, str)  :
                return obj in self._mydict["members"]
            elif isinstance(obj, _IsyNodeBase)  :
                return obj._get_prop("address") in self._mydict["members"]
        return False

    def member_add(self, node, flag=0) :
	r = self.isy.soapcomm("SetParent",
		node=node._get_prop("address"), nodeType=node.nodeType(),
		parent=self._mydict["address"], parentType=self.nodeType())

    def _rename(self, cmd,  newname) :
        if self.debug & 0x01 :
	    print("rename : ", self.__class__.__name__, " : ", newname)
	#if not isinstance(newname, str) or len(newname) == 0 :
	#    print "newname : ", newname
	#    raise IsyTypeError("rename : name value not str")
	r = self.isy.soapcomm(cmd,
			id=self._mydict["address"], name=newname )

	return r

    # check if scene _contains_ node
    def __contains__(self, other):
            return self.is_member(other)


    # check if obj _contains_  attib
#    def __contains__(self, other):
#       if isinstance(other, str)  :
#           return other in self._getlist
#       else :
#           return False


#    class MemberDicte(dict):
#
#	def __getitem__(self, key):
#	    val = dict.__getitem__(self, key)
#	    print 'GET', key
#	    return val
#
#	def __setitem__(self, key, val):
#	    print 'SET', key, val
#	    dict.__setitem__(self, key, val)
#
#	def __delitem__(self, key):
#	    print 'DEL', key
#	    dict.__delitem__(self, key)
#
#	def __repr__(self):
#	    dictrepr = dict.__repr__(self)
#	    return '%s(%s)' % (type(self).__name__, dictrepr)
#
#	def get(self, key, default_val):
#	    print 'GET', key, default_val
#	    dict.get(self, key, default_val)
#	
#	def update(self, *args, **kwargs):
#	    print 'update', args, kwargs
#	    for k, v in dict(*args, **kwargs).iteritems():
#		self[k] = v



#
# convers a node Id  to a int
# eg: "9 4A 5F 2" => 00001001010010100101111100000010 => 155868930
#
def node_id_to_int(h) :
    a = h.split(' ')
    return  ( int(a[0], 16) << 24 ) | ( int(a[1], 16) << 16 ) | \
		    ( int(a[2], 16) << 8 ) | int(a[3], 16)



# def rate
# def onlevel
class IsyNode(_IsyNodeBase):
    """ Node Class for ISY

        Attributes :
            status / ST
            ramprate / RR
            onlevel / OL

        Readonly Attributes :
            address
            formatted
            enabled
            pnode
            type
            name
            ELK_ID
            flag

        funtions:
	    get_rr:
	    set_rr:

    Bugs: Results are undefined for Node class objects that
	    represent a deleteed node 

    """
    _getlist = ['address', 'enabled', 'formatted',
            'ELK_ID',
	    'parent', 'parent-type',
            'name', 'pnode', 'flag', 'wattage',
            'OL', 'RR', 'ST', 'type']
    _setlist = ['RR', 'OL', 'status', 'ramprate', 'onlevel', 'enable']
    _propalias = {'status': 'ST', 'value': 'ST', 'val': 'ST',
            'id': 'address', 'addr': 'address',
            'ramprate': 'RR', 'onlevel': 'OL',
            "node-flag": "flag"}
    #_boollist = [ "enabled" ]

    def __init__(self, isy, ndict) :

	# self._objtype = (1, "node")
	self._objtype = "node"

	super(self.__class__, self).__init__(isy, ndict)

#        if not self.isy.eventupdates :
#            #update only nodes
#            if "node-flag" in self._mydict :
#                self.update()

	self._hash = node_id_to_int(self._mydict["address"])

        if self.debug & 0x01 :
            print("Init Node : \"" + self._mydict["address"] + \
                "\" : \"" + self._mydict["name"] + "\"")
            # self.isy._printdict(self.__dict__)


    # Special case from BaseClass due to ST/RR/OL props
    def _get_prop(self, prop):

        # print "IN get_prop ", prop

        if prop == "formatted" :
            prop = "ST"
            value = "formatted"
        else :
            value = "value"

        if prop in self._propalias :
            prop = self._propalias[prop]

        if not prop in self._getlist :
#	    if prop in ['parent', 'parent-type'] :
#		return None
            raise IsyPropertyError("no property Attribute {!s}".format(prop))

        # check if we have a property

        if prop in ['ST', 'OL', 'RR'] :
            # Scene's do not have property values

            if prop in self._mydict["property"] :
                # print self._mydict["property"]
                # print "prop value", prop, value
                return self._mydict["property"][prop][value]
            else :
                return None

#            if self._mydict["property"]["time"] == 0 :
#                    self.update()
#            elif self.isy.cachetime :
#                if time.gmtime() < (self.cachetime + self._mydict["property"]["time"] ) :
#                    self.update()

        else :

#            if prop in self._mydict :
#		if prop in self._boollist :
#		    return(val2bool(self._mydict[prop])) 
#		else :
#		    return self._mydict[prop]
#            else :
#                return None

	    return super(self.__class__, self)._get_prop(prop)

    def _set_prop(self, prop, new_value):
        """  generic property set """
        # print "IN set_prop ", prop, new_value
        if self.debug & 0x04 :
            print("_set_prop ", prop, " : ", new_value)

        if prop in self._propalias :
            prop = self._propalias[prop]

        if not prop in self._setlist :
	    if prop == "ST" :
		self.on(new_value)
		return
	    else :
		raise IsyPropertyError("_set_prop : " \
		    "Invalid property Attribute " + prop)

        if prop == 'enable' :
	    self._mydict[prop] = bool(new_value)
	    self.isy.node_enable(self._mydict["address"], bool(new_value))

        elif prop in ['OL', 'RR'] :
            if not str(new_value).isdigit :
                raise IsyTypeError("Set Property : Bad Value : node=%s prop=%s val=%s" %
                            self._mydict["address"], prop, str(new_value))


	    self.isy._node_send(self._mydict["address"], "set", prop, str(new_value))

            # self._mydict["property"]["time"] = 0

            if prop in self._mydict["property"] :
                # if isinstance(new_value, (int, float))  : # already checked with isdigit
		self._mydict["property"][prop]["value"] = new_value

        # we need to tie this to some action
        elif prop in self._mydict :
            # self._mydict[prop] = new_value
            pass
        else :
            #print "_set_prop AttributeError"
            raise AttributeError("no Attribute " + prop)


    def _gettype(self):
        """  Type of Node (readonly) """
        return "node"

    # enable node
    def get_enable(self):
        """ get enable/disable status a node """
        return self._get_prop("enable")

    def set_enable(self, new_bool):
        """ Set enable status a node

	    args:
		enable bool
	"""
        return self._set_prop("enable", new_bool)

    enable = property(get_enable, set_enable, None, "enable/disable a node")

    def get_wattage(self):
        """ get wattage """
        return self._get_prop("wattage")

    def set_wattage(self, watts):
	""" set wattage property """
	return self.isy.node_set_powerinfo( self._mydict["address"], wattage=watts)
    wattage = property(get_wattage, set_wattage)




    # ramprate property
    # obj mathod for getting/setting a Node's value
    # sets how fast a light fades on.
    def get_rr(self):
        """ Get/Set RampRate property of Node """
        return self._get_prop("RR")

    def set_rr(self, new_value):
        """ Get/Set RampRate property of Node """
        return self._set_prop("RR", new_value)

    ramprate = property(get_rr, set_rr)

    # On Level property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    # when turned on
    def get_ol(self):
        """ Get/Set On Level property of Node """
        return self._get_prop("OL")

    def set_ol(self, new_value):
        """ Get/Set On Level property of Node """
        return self._set_prop("OL", new_value)
    onlevel = property(get_ol, set_ol)


#    def get_fm(self):
#       """ property On Level Value of Node """
#        return self._get_prop("formatted")
#    formatted = property(get_fm)

    # status property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    def get_status(self):
        """ Get/Set Status property of Node """
        return self._get_prop("ST")
    def set_status(self, new_value):
        """ Get/Set Status property of Node """
        return self.on(new_value)
    status = property(get_status, set_status)


    #
    # readonly to node attribute
    #



    def rename(self, newname) :
	return  self._rename("RenameNode",  newname) 


    #
    #
    #
    def update(self) :
        """ force object to manualy update it's propertys """
        xurl = "/rest/nodes/" + self._mydict["address"]
        if self.debug & 0x01 :
            print("_updatenode pre _getXML")
        _nodestat = self.isy._getXMLetree(xurl)
        # del self._mydict["property"]["ST"]
        for prop in _nodestat.iter('property'):
            tprop = dict()
            for k, v in list(prop.items()) :
                tprop[k] = v
            if "id" in tprop :
                self._mydict["property"][tprop["id"]] = tprop
        # self._mydict["property"]["time"] = time.gmtime()

    # experimental
    def __bool__(self) :
        #print "__nonzero__ call", self._mydict["property"]["ST"]["value"], \
        #        " :: ", int(self._mydict["property"]["ST"]["value"])
        return(bool(self._mydict["property"]["ST"]["value"]) > 0)

    # use the node address as the hash value
    def __hash__(self) :
	return( self._hash )


#    def __str__(self):
#       print "__str__ call"
#       return("my str : " + self._mydict["name"])

    def __float__(self):
        # print "__float__ call"
        return float(int(self._mydict["property"]["ST"]["value"]) / float(255))

class IsyScene(_IsyNodeBase):
    """ Node Group Class for ISY

        writeonly attributes :
            status

        readonly attributes :
            address
            name
            flag
            deviceGroup
            parent
            parent-type
            ELK_ID
    """
    _getlist = ['address', 'name', "ELK_ID", "deviceGroup",
                'flag', 'parent', 'parent-type']
    _setlist = []
    _propalias = {'id': 'address', 'addr': 'address',
                    "group-flag": "flag"}

    def __init__(self, *args):
	#self._objtype = (2, "scene")
	self._objtype = "scene"
	super(self.__class__, self).__init__(*args)

    # status property
    # obj mathod for getting/setting a  Scene's value
    # where in most cases light is how bright the light is
    def set_status(self, new_value):
        """ set status value of Scene """
        return self._set_prop("ST", new_value)

    status = property(None, set_status)


    def _getmembers(self) :
        """ List members of a scene or group """
        if "members" in self._mydict :
            return self._mydict["members"].keys()
        else :
            return None
    members = property(_getmembers)

    def member_list(self) :
        return self._getmembers()

    def is_member(self, obj) :
        if "members" in self._mydict :
            if isinstance(obj, str)  :
                return obj in self._mydict["members"]
            elif isinstance(obj, _IsyNodeBase)  :
                return obj._get_prop("address") in self._mydict["members"]
        return False

    def rename(self, newname) :
	""" rename node/scene/folder """
	return  self._rename("RenameGroup",  newname)

    def member_del(self, node) :
	r = self.isy.soapcomm("RemoveFromGroup",
		node=node._get_prop("address"),
		group=self._mydict["address"])

    def member_add(self, node, flag=16) :
	r = self.isy.soapcomm("MoveNode",
		node=node._get_prop("address"),
		group=self._mydict["address"],
		flag=16)
	return r

    def member_iter(self, flag=0):
	""" iter though members
	    Folders iter though their contents (nodes/scenes/folders)
	    Scene iter though their members	(nodes)
	    Nodes iter though sub-nodes		(nodes)
	"""
        if "members" in self._mydict :
            for k in list(self._mydict["members"].keys()) :
                if flag and not(flag & self._mydict["members"][k]) :
                    continue
                else :
                    yield k

    def __iter__(self):
        return self.member_iter()

    # check if scene _contains_ node
    def __contains__(self, other):
            return self.is_member(other)



class IsyNodeFolder(_IsyNodeBase):
    """ Node Folder Class for ISY

        readonly attributes :
            address
            name
            flag
    """
    _getlist = ['address', 'name', 'flag']
    _setlist = []
    _propalias = {'id': 'address', 'addr': 'address', "folder-flag": "flag"}

    def __init__(self, *args):
	#self._objtype = (3, "folder")
	self._objtype = "folder"
	super(self.__class__, self).__init__(*args)

    def member_add(self, node, flag=0) :
	""" add Node/Scene or Folder to Folder Obj

		 Args:
		    node = address, name or Node/Scene/Folder Obj

	      sets Parent for node/scene/folder to current Obj Folder

	    calls SOAP SetParent()
	"""
	r = self.isy.soapcomm("SetParent",
		node=node._get_prop("address"), nodeType=node.nodeType(),
		parent=self._mydict["address"], parentType=self.nodeType())
	return r

    def member_del(self, node) :
	""" del Node/Scene or Folder to Folder Obj

		 Args:
		    node = address, name or Node/Scene/Folder Obj

	      del node/scene/folder to current Obj Folder
	      (and moves to base folder)

	    calls SOAP SetParent()
	"""
	r = self.isy.soapcomm("SetParent",
		node=node._get_prop("address"), nodeType=node.nodeType())
	return r

    def rename(self, newname) :
	""" renames current Obj Folder

	    args :
		name = new folder name

	    calls SOAP RenameFolder()
	"""
	return self._rename("RenameFolder",  newname)


    def __iter__(self):
        return self.member_iter()

    def __contains__(self, other):
        pass

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
