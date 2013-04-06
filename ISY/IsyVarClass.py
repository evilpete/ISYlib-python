

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
            get_var_ts() :      get timestamp
            get_var_type() :    get Var type
            get_var_init() :    get  inital value for Var
            set_var_init(new_value) :   set inital value for Var
            get_var_value() :   get current value
            set_var_value(new_value) :  set new value for Var
            get_var_id() :      get unique for Var used by ISY
            get_var_name() :    get name of var

    """

    _getlist = ['id', 'type', 'init', 'val', 'ts', 'name']
    _setlist = ['init', 'val']
    _propalias = {'value': 'val', 'status': 'val', 'addr': 'id', 'address': 'id'}

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
        return self._get_prop("init")

    def set_var_init(self, new_value):
        """ sets var init value
        this can also be set via the property : init
        """
        self.isy._var_set_value(self._mydict['id'], new_value, "init")

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
        self.isy._var_set_value(self._mydict['id'], new_value)
    value = property(get_var_value, set_var_value)

#    def get_var_id(self):
#       return self._get_prop("id")
#    id = property(get_var_id)

#    def get_var_name(self):
#       return self._get_prop("name")
#    name = property(get_var_name)


    def __int__(self) : return int(self._mydict["val"])

    def __str__(self) : return str(self._mydict["val"])

    def __bool__(self) : return int( self._mydict["val"]) != 0

    # NotImplemented
    def __cast(self, other):
        if isinstance(other, self.__class__): return other._mydict["val"]
	if isinstance(other, str) and other.isdigit() : return int( other )
        else: return other

    def bit_length(self): return bit_length(self._mydict["val"])

    #
    # Type conversion
    def __str__(self): return str(self._mydict["val"])
    def __long__(self): return long(self._mydict["val"])
    def __float__(self): return float(self._mydict["val"])
    def __int__(self):
	return int(self._mydict["val"])

    def __abs__(self): return abs(self._mydict["val"])

    # 
    def __lt__(self, other): return self._mydict["val"] <  self.__cast(other)
    def __le__(self, other): return self._mydict["val"] <= self.__cast(other)
    def __eq__(self, other): return self._mydict["val"] == self.__cast(other)
    def __ne__(self, other): return self._mydict["val"] != self.__cast(other)
    def __gt__(self, other): return self._mydict["val"] >  self.__cast(other)
    def __ge__(self, other): return self._mydict["val"] >= self.__cast(other)

    def __cmp__(self, other):
        return cmp(self._mydict["val"], self.__cast(other))


    def __add__(self, other):
	print "__add__"
        if isinstance(other, self.__class__):
            return (self._mydict["val"] + other._mydict["val"])
        elif isinstance(other, type(self._mydict["val"])):
            return (self._mydict["val"] + other)
        else:
            return (self._mydict["val"] + other)

    __radd__ = __add__

    def __iadd__(self, other):
	print "__iadd__"
        if isinstance(other, self.__class__): self._mydict["val"] += other._mydict["val"]
        else: self._mydict["val"] += int(other)
        return self

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return (self._mydict["val"] - other._mydict["val"])
        elif isinstance(other, type(self._mydict["val"])):
            return (self._mydict["val"] - int(other))

    def __isub__(self, other):
        if isinstance(other, self.__class__): self._mydict["val"] -= other._mydict["val"]
        else: self._mydict["val"] -= int(other)
        return self

    # Mult &  div
    #
    def __mul__(self, n): return (self._mydict["val"]*n)
    __rmul__ = __mul__

    def __imul__(self, n):
	self._mydict["val"] *= n
        return self

    def __div__(self, n): return (self._mydict["val"] / n)

    def __floordiv__(self, other): return self._mydict["val"] // self.__cast(other)
    def __ifloordiv__(self, n):
	self._mydict["val"] //= n
        return self

    def __itruediv__(self, n):
	self._mydict["val"] /= int(n)
	return self

    def __imod__(self, n):
	self._mydict["val"] %= n
        return self

    def __ipow__(self, n):
	self._mydict["val"] **= n
        return self

    # logic opts
    def __and__(self, n): return self._mydict["val"] & self.__cast(n)
    def __iand__(self, n): 
	self._mydict["val"] &= n
	return self
    def __or__(self, other): return self._mydict["val"] | self.__cast(other)
    __ror__ = __or__
    def __ior__(self, other):
	self._mydict["val"] |= self.__cast(other)
	return self
    def __ixor__(self, other):
	self._mydict["val"] ^= self.__cast(other)
	return self
    def __xor__(self, other): return self._mydict["val"] ^ self.__cast(other)

    def __invert__(self): return ~ self._mydict["val"] 

    def __irshift__(self, other):
	self._mydict["val"] >>= self.__cast(other)
	return self
    def __ilshift__(self, other):
	self._mydict["val"] >>= self.__cast(other)
	return self


    def __bool__(self): return (self._mydict["val"] != 0)

    def __format__(self, spec): return int(self._mydict["val"]).__format__(spec)




#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
