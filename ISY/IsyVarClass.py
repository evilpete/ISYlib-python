

from IsyExceptionClass import *
from IsyUtilClass import *

__all__ = ['IsyVar']

class IsyVar(IsySubClass):
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
    getlist = ['id', 'type', 'init', 'val', 'ts', 'name' ]
    setlist = ['init', 'val']
    propalias = { 'value': 'val',
			    'status': 'val',
			    'addr': 'id'
			    }


    def get_var_ts(self):
	""" returns var timestamp
	this is also avalible via the property : ts
	"""
	return self._get_prop("ts")
    ts = property(get_var_ts)

    def get_var_type(self):
	""" returns var timestamp
	this is also avalible via the property : type
	"""
	return self._get_prop("type")
    type = property(get_var_type)

    def get_var_init(self):
	""" returns var init value
	this is also avalible via the property : init
	"""
	return self._get_prop("init")
    def set_var_init(self, new_value):
	""" sets var init value
	this can also be set via the property : init
	"""
	isy._set_var_value(self._mydict['id'], new_value, 1)
    init = property(get_var_init, set_var_init)
    """ init property
    this value can also be read or set
    """

    def get_var_value(self):
	""" returns var value
	this is also avalible via the property : value
	"""
	return self._get_prop("val")
    def set_var_value(self, new_value):
	""" sets var value
	this can also be set via the property : value
	"""
	isy._set_var_value(self._mydict['id'], new_value)
    value = property(get_var_value, set_var_value)
    """ value property
    this can also be read or set
    """

    def get_var_id(self):
	return self._get_prop("id")
    id = property(get_var_id)

    def get_var_name(self):
	return self._get_prop("name")
    name = property(get_var_name)



#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)

