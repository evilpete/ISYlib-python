

from IsyUtilClass import IsyUtil
from IsyExceptionClass import *
# from IsyClass import *
# from IsyNodeClass import *
#from IsyProgramClass import *
# from IsyVarClass import *


__all__ = ['IsyNode']

# def rate
# def onlevel
class IsyNode(IsyUtil):
    """ Node Class for ISY
	attributes :
	ramprate onlevel status address name type members
    """

    def __init__(self, isy, ndict) :
        if isinstance(ndict, dict):
            self._nodedict = ndict
        else :
            print "error : class IsyNode called without ndict"
            raise TypeError("IsyNode: called without ndict")

        if isinstance(isy, IsyUtil):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class IsyNode called without isyUtilClass"
            raise TypeError("IsyNode: isy is wrong class")
        # only update if not a scene
        if not (int(self._nodedict["flag"]) & 0x04) :
            self.update()

        if self.debug & 0x01 :
	    print "Init Node : \"" + self._nodedict["address"] + \
		"\" : \"" + self._nodedict["name"] + "\""
        #self._printdict(self._nodedict)

	self.getlist = ['address', 'enabled', 'formatted',
			'members', 'name', 'pnode', 'flag',
			'OL', 'RR', 'ST', 'type']

	self.setlist = ['ST', 'RR', 'OL', 'status', 'ramprate', 'onlevel' ]
	self.propalias = { 'status': 'ST',
			'ramprate': 'RR',
			'onlevel': 'OL'  }


    def _get_node_prop(self, prop):
        """  generic property get """
        # print "----get_status call"

	if prop == "formatted" :
	    prop = "ST"
	    value = "formatted"
	else :
	    value = "value"

	if prop in self.propalias :
	    prop = self.propalias[prop]

	if prop == 'type' and int(self._nodedict["flag"]) & 0x04 :
            return "scene"

        if not prop in self.getlist :
	    raise IsyPropertyError("no property Attribute " + prop)

        # check if we have a property

        if prop in ['ST', 'OL', 'RR'] :
	    # Scene's do not have property values
	    if int(self._nodedict["flag"]) & 0x04 :
		return None

	    if prop in self._nodedict["property"] :
		return self._nodedict["property"][prop][value]
	    else :
		return None

#            if self._nodedict["property"]["time"] == 0 :
#                    self.update()
#            elif self.isy.cachetime :
#                if time.gmtime() < ( self.cachetime + self._nodedict["property"]["time"] ) :
#                    self.update()

        else :

	    if prop in self._nodedict :
		return self._nodedict[prop]
	    else :
		return None

    def _set_node_prop(self, prop, new_value):
        """  generic property set """
        if self.debug & 0x04 :
            print "_set_node_prop ", prop, " : ", new_value

        if not str(new_value).isdigit :
            TypeError("Set Property : Bad Value : node=%s prop=%s val=%s" %
				    self._nodedict["address"], prop, str(val))

        self.isy._node_set_prop(self._nodedict["address"], prop, str(new_value))

        self._nodedict["property"]["time"] = 0

        try:
            self._nodedict["property"][prop]
        except:
            pass
            #print "_set_node_prop AttributeError"
            #raise AttributeError("no Attribute " + prop)
        else:
            if isinstance(new_value, (long, int, float))  :
                self._nodedict["property"][prop]["value"] = new_value

        # exception TypeError
        # print "set_status NOT VALID: ", new_value
        # raise NameError('New Val not a number')


    # ramprate property
    # obj mathod for getting/setting a Node's value
    # sets how fast a light fades on.
    def get_node_rr(self):
	"""
	Get RampRate property of Node
	:rtype: str
        :return: RampRate value
	"""
        return self._get_node_prop("RR")

    def set_node_rr(self, new_value):
	"""
	set_node_rr : Get/Set RampRate property of Node
	"""
        return self._set_node_prop("RR", new_value)

    ramprate = property(get_node_rr, set_node_rr)
    """
    ramprate Get/Set RampRate property of Node
    """

    # On Level property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    # when turned on
    def get_node_ol(self):
	""" property On Level Value of Node """
        return self._get_node_prop("OL")

    def set_node_ol(self, new_value):
        return self._set_node_prop("OL", new_value)
    onlevel = property(get_node_ol, set_node_ol)


    def get_node_fm(self):
	""" property On Level Value of Node """
        return self._get_node_prop("formatted")
    formatted = property(get_node_fm)

    # status property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    def get_node_status(self):
	""" property status value of Node """
        return self._get_node_prop("ST")

    def set_node_status(self, new_value):
        return self._set_node_prop("ST", new_value)

    status = property(get_node_status, set_node_status)
    """  returns status of Node """


    #
    # readonly to node attribute
    #
    def _getaddr(self):
        return self._nodedict["address"]
    address = property(_getaddr)

    def _getname(self):
	""" property : Name of Node (readonly) """
        return self._nodedict["name"]
    name = property(_getname)

    def _gettype(self):
        if "type" in self._nodedict :
            return self._nodedict["type"]
        elif int(self._nodedict["flag"]) & 0x04 :
            return "scene"
        else :
            return "_gettype : ERROR"
    type = property(_gettype)

    def _getmembers(self) :
	""" property : List members of a scene or group """
        if "members" in self._nodedict :
            return self._nodedict["members"]
        else :
            return None
    members = property(_getmembers)
    """
    Get members list for Scene
    :rtype: list
    :return: list of Nodes
    """

    def scene_nodes(self) :
        pass

    def pdict(self):
        self._printdict(self._nodedict)


    #
    #
    # direct (non obj) call to get value
    #
    def value(self) :
        try:
            return self._nodedict["property"]["ST"]["value"]
        except:
            return None
        #else:
        #    return self._nodedict["property"]["ST"]["value"]

    # direct (non obj) call to set value
    def svalue(self, v) :
        try:
            self._nodedict["property"]["ST"]["value"]
        except:
            return None
        else:
            self._nodedict["property"]["ST"]["value"] = v


    def on(self) :
        self.isy._node_comm(self._nodedict["address"], "DON")
        try :
            self._nodedict["property"]["time"] = 0
        except :
            pass
        # self.update()

    def off(self) :
        self.isy._node_comm(self._nodedict["address"], "DOF")

        try :
            self._nodedict["property"]["ST"]["value"] = 0
            self._nodedict["property"]["time"] = 0
        except:
            pass


    def beep(self) :
        self.isy._node_comm(self._nodedict["address"], "BEEP")
        pass

    #
    #
    #
    def update(self) :
        xurl = "/rest/nodes/" + self._nodedict["address"]
        if self.debug & 0x01 :
            print "_updatenode pre _getXML"
        _nodestat = self.isy._getXMLetree(xurl)
        # del self._nodedict["property"]["ST"]
        for prop in _nodestat.iter('property'):
            tprop = dict ( )
            for k, v in prop.items() :
                tprop[k] = v
            if "id" in tprop :
                self._nodedict["property"][tprop["id"]] = tprop
        # self._nodedict["property"]["time"] = time.gmtime()

    def __getitem__(self, prop):
	return self._get_node_prop(prop)

    def __setitem__(self, prop, val):
        if not prop in ['ST', 'OL', 'RR'] :
            raise IsyProperyError("__setitem__: unknown propery : " + str(prop) )
        self._set_prop(prop, val)
        # self._nodedict["property"]["time"] = 0

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )

    # The following is experimental

    def __nonzero__(self) :
        #print "__nonzero__ call", self._nodedict["property"]["ST"]["value"], \
        #        " :: ", int(self._nodedict["property"]["ST"]["value"])
        return ( int(self._nodedict["property"]["ST"]["value"]) > 0 )

    def __get__(self, instance, owner):
        print "__get__ call"
        return self.value()

    def __set__(self, instance, value):
        print "__set__ call"
        self._set_prop("ST", val)

    def __iter__(self):
	for p in self.getlist :
	    yield (p , self._get_node_prop(p))


#    def __str__(self):
#       print "__str__ call"
#       return ( "my str : " + self._nodedict["name"] )

    def __repr__(self):
        return "<IsyNode %s @ %s at 0x%x>" % (self._nodedict["address"], self.isy.addr, id(self))

    def __float__(self):
        # print "__float__ call"
        return float ( int(self._nodedict["property"]["ST"]["value"]) / float(255) )

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
