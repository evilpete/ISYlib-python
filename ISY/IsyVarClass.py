""" Obj Class Isy veriable entries """

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"


from ISY.IsyExceptionClass import *
from ISY.IsyUtilClass import IsySubClass

__all__ = ['IsyVar']

class IsyVar(IsySubClass):
    """ VAR Class for ISY

        attributes/properties :
            ts :        timetamp
            type :      Var Type
            init :      inital value for Var ( at ISY boot )
            value :     current value
            id :        unique for Var used by ISY
            name :      name of var

        funtions:
            get_var_init() :    get  inital value for Var
            set_var_init(new_value) :   set inital value for Var
            get_var_value() :   get current value
            set_var_value(new_value) :  set new value for Var

    """

    _getlist = ['id', 'type', 'init', 'val', 'ts', 'name']
    _setlist = ['init', 'val']
    _propalias = {'value': 'val', 'status': 'val', 'addr': 'id', 'address': 'id'}
    # _objtype = (-1, "var")
    _objtype = "var"

# Var :    {  '1:1': {  'id': '1:1', 'init': '0', 'name': 'enter_light',
#          'ts': '20130114 14:33:35', 'type': '1', 'val': '0'}

#    def get_var_ts(self):
#       """ returns var timestamp
#       this is also avalible via the property : ts
#       """
#       return self._get_prop("ts")
#    ts = property(get_var_ts)

#    def get_var_type(self):
#       """ returns var timestamp
#       this is also avalible via the property : type
#       """
#       return self._get_prop("type")
#    type = property(get_var_type)

    def get_var_init(self):
        """ returns var init value
        this is also avalible via the property : init
        """
        return self._mydict["init"]

    def set_var_init(self, new_value):
        """ sets var init value
        this can also be set via the property : init
        """
	if new_value == self._mydict["init"] :
	    return
        self.isy._var_set_value(self._mydict['id'], new_value, "init")

    init = property(get_var_init, set_var_init)


    def refresh(self):
	"reload val from isy"
	return self.isy.var_refresh_value(self._mydict["id"])

    def get_var_value(self):
        """ returns var value
        this is also avalible via the property : value
        """
        return self._mydict["val"]
    def set_var_value(self, new_value):
        """ sets var value
        this can also be set via the property : value
        """
	if new_value == self._mydict["val"] :
	    return
        self.isy._var_set_value(self._mydict['id'], new_value)
    value = property(get_var_value, set_var_value)

    def get_callback(self) :
	return self.isy.callback_get(self._mydict["id"])
    def set_callback(self, func, *args) :
	if func == None :
	    return self.isy.callback_del(self._mydict["id"])
	else :
	    return self.isy.callback_set(self._mydict["id"], func, args)
    callback = property(get_callback, set_callback)

#    def get_var_id(self):
#       return self._get_prop("id")
#    id = property(get_var_id)

#    def get_var_name(self):
#       return self._get_prop("name")
#    name = property(get_var_name)


#    def rename(self, newname) :
#	self.isy.call_soap_method("RenameNode",
#			self._mydict["address"], newwname)

    # Not fully Implemented
    def __cast(self, other):
        if isinstance(other, self.__class__): return other._mydict["val"]
	if isinstance(other, str) and other.isdigit() : return int( other )
        else: return other

    def bit_length(self): return int(self._mydict["val"]).bit_length()

    #
    # Type conversion
    def __str__(self): return str(self._mydict["val"])
    # Type conversion
    def __long__(self): return long(self._mydict["val"])
    # Type conversion
    def __float__(self): return float(self._mydict["val"])
    # Type conversion
    def __int__(self): return int(self._mydict["val"])
    # Type conversion
    def __bool__(self) : return bool( self._mydict["val"]) != 0

    # mathematical operator
    def __abs__(self): return abs(self._mydict["val"])

    #  comparison functions 
    def __lt__(self, n): return self._mydict["val"] <  self.__cast(n)
    #  comparison functions 
    def __le__(self, n): return self._mydict["val"] <= self.__cast(n)
    #  comparison functions 
    def __eq__(self, n): return self._mydict["val"] == self.__cast(n)
    #  comparison functions 
    def __ne__(self, n): return self._mydict["val"] != self.__cast(n)
    #  comparison functions 
    def __gt__(self, n): return self._mydict["val"] >  self.__cast(n)
    #  comparison functions 
    def __ge__(self, n): return self._mydict["val"] >= self.__cast(n)
    #  comparison functions 

    #  comparison functions 
    def __cmp__(self, n): return cmp(self._mydict["val"], self.__cast(n))


    # mathematical operator
    def __add__(self, n):
	#print "__add__"
        if isinstance(n, self.__class__):
            return (self._mydict["val"] + n._mydict["val"])
        elif isinstance(n, type(self._mydict["val"])):
            return (self._mydict["val"] + n)
        else:
            return (self._mydict["val"] + n)

    __radd__ = __add__

    # mathematical operator
    def __iadd__(self, n):
        if isinstance(n, self.__class__): self._mydict["val"] += n._mydict["val"]
        else: self._mydict["val"] += int(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
        return self

    # mathematical operator
    def __sub__(self, n):
        if isinstance(n, self.__class__):
            return (self._mydict["val"] - n._mydict["val"])
        elif isinstance(n, type(self._mydict["val"])):
            return (self._mydict["val"] - int(n))

    # mathematical operator
    def __isub__(self, n):
        if isinstance(n, self.__class__): self._mydict["val"] -= n._mydict["val"]
        else: self._mydict["val"] -= int(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
        return self

    # Mult &  div

    # mathematical operator
    def __mul__(self, n): return (self._mydict["val"]*n)
    __rmul__ = __mul__

    def __imul__(self, n):

    # mathematical operator
	self._mydict["val"] *= n
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
        return self

    def __floordiv__(self, n): return self._mydict["val"] // self.__cast(n)

    # mathematical operator

    def __ifloordiv__(self, n):

    # mathematical operator
	self._mydict["val"] = self._mydict["val"] // n
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
        return self

    def __truediv__(self, n): return (self._mydict["val"] / self.__cast(n))

    # mathematical operator
    __div__ = __truediv__

    def __itruediv__(self, n):

    # mathematical operator
	self._mydict["val"] /= self.__cast(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self
    __idiv__ = __itruediv__

    def __imod__(self, n):

    # mathematical operator
	self._mydict["val"] %= self.__cast(n) 
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
        return self

#   def __ipow__(self, n):
    # mathematical operator
#	self._mydict["val"] **= self.__cast(n) 
#	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
#        return self

    def __neg__(self): return - self._mydict["val"]

    # mathematical operator

    # logic opts
    def __and__(self, n): return self._mydict["val"] & self.__cast(n)

    def __iand__(self, n): 
	self._mydict["val"] &= self.__cast(n) 
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self

    def __or__(self, n): return self._mydict["val"] | self.__cast(n)
    __ror__ = __or__

    def __ior__(self, n):
	self._mydict["val"] |= self.__cast(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self

    def __ixor__(self, n):
	self._mydict["val"] ^= self.__cast(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self

    def __xor__(self, n): return self._mydict["val"] ^ self.__cast(n)

    def __invert__(self): return ~ self._mydict["val"] 

    def __irshift__(self, n):
	self._mydict["val"] >>= self.__cast(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self

    def __ilshift__(self, n):
	self._mydict["val"] >>= self.__cast(n)
	self.isy._var_set_value(self._mydict['id'], self._mydict["val"])
	return self



    #def __format__(self, spec): return int(self._mydict["val"]).__format__(spec)

    def __repr__(self):
        return "<%s %s at 0x%x>" % (self.__class__.__name__, self.isy.addr, id(self))

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
