

from IsyExceptionClass import *
from IsyUtilClass import *

__all__ = ['IsyVar']

class IsyVar(IsyUtil):
    """ VAR Class for ISY

	attributes/properties :
	    ts :	timetamp 
	    type :	Var Type
	    init :	inital value for Var ( at ISY boot )
	    value :	current value
	    id :	unique for Var used by ISY
	    name :	name of var

	funtions:
	    get_var_ts() :	get timestamp
	    get_var_type() :	get Var type
	    get_var_init() :	get  inital value for Var
	    set_var_init(new_value) :	set inital value for Var
	    get_var_value() :	get current value
	    set_var_value(new_value) :	set new value for Var
	    get_var_id() :	get unique for Var used by ISY
	    get_var_name() :	get name of var

    """

    def __init__(self, isy, vdict) :
	""" INIT IsyVar """

        if isinstance(vdict, dict):
            self._mydict = vdict
        else :
            print "error : class IsyVar called without vdict"
            raise IsyValueError("IsyVar: called without vdict")

        if isinstance(isy, IsyUtil):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class IsyVar called without Isy"
            raise TypeError("IsyVar: isy is wrong class")

        if self.debug & 0x04 :
	    print "IsyVar: ",
	    self._printdict(self._mydict)

	self.getlist = ['id', 'type', 'init', 'val', 'ts', 'name' ]
	self.setlist = ['init', 'val']
	self.propalias = { }

    def _get_var_prop(self, prop):
	if prop in self.propalias :    
	    prop = self.propalias[prop]

	if prop in self.getlist : 
	    if prop in self._mydict :
		return(self._mydict[prop])
	return(None)

    def _set_var_prop(self, prop, val):
	if prop in self.setlist :
	    pass
	else :
            raise IsyPropertyError("_set_var_prop : "
	    	    "no property Attribute " + prop)

    def get_var_ts(self):
	""" returns var timestamp
	this is also avalible via the property : ts
	"""
	return(self._mydict["ts"])
    ts = property(get_var_ts)

    def get_var_type(self):
	""" returns var timestamp
	this is also avalible via the property : type
	"""
	a = self._mydict["id"].split(':')
	return(a[1])
    type = property(get_var_type)

    def get_var_init(self):
	""" returns var init value
	this is also avalible via the property : init
	"""
	return(self._mydict["init"])
    def set_var_init(self, new_value):
	""" sets var init value
	this can also be set via the property : init
	"""
	pass
    init = property(get_var_init, set_var_init)
    """ init property
    this value can also be read or set
    """

    def get_var_value(self):
	""" returns var value
	this is also avalible via the property : value
	"""
	return(self._mydict["val"])
    def set_var_value(self, new_value):
	""" sets var value
	this can also be set via the property : value
	"""
	pass
    value = property(get_var_value, set_var_value)
    """ value property
    this can also be read or set
    """

    def get_var_id(self):
	return(self._mydict["id"])
    id = property(get_var_id)

    def get_var_name(self):
	return(self._mydict["name"])
    name = property(get_var_name)

    def __getitem__(self, prop):
	return self._get_var_prop(prop)

    def __setitem__(self, prop):
	return self._set_var_prop(prop)

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )
	pass

    def __get__(self, instance, owner):
	return self._get_var_prop("val")
    def __set__(self,  val):
	self.set_var_value(val)

    def __iter__(self):
	for p in self.getlist :
	    if p in self._mydict :
		yield (p , self._mydict[p])
	    else :
		yield (p , None)

#    def __repr__(self):
#	pass


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)

