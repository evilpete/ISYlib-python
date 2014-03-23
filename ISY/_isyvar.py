"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"


from ISY.IsyVarClass import IsyVar
from ISY.IsyExceptionClass import IsyValueError, IsyResponseError, IsyPropertyError, IsyRuntimeWarning, IsyWarning

import xml.etree.ElementTree as ET
from warnings import warn 


# import pprint

##
## variable funtions
##
def load_vars(self) :
    """ Load variable names and values

        args : none

        internal function call

    """
    if not hasattr(self, '_vardict') or not isinstance(self._vardict, dict):
        self._vardict = dict ()

    if not hasattr(self, '_name2id') or not isinstance(self._name2id, dict):
        self._name2id = dict ()

    self.name2var = dict ()
    for t in [ '1', '2' ] :
        vinfo = self._getXMLetree("/rest/vars/get/" + t)
        for v in vinfo.iter("var") :
            vdat = dict ()
            for vd in list(v) :
                if vd.tag != "var" :
                    vdat[vd.tag] = vd.text
            vdat["val"] = int(vdat["val"])
            vdat["init"] = int(vdat["init"])
            self._vardict[t + ":" + v.attrib["id"]] = vdat
        # self._printdict(self._vardict)

        vinfo = self._getXMLetree("/rest/vars/definitions/" + t)
        for v in vinfo.iter("e") :
            # self._printinfo(v, "e :")
            vid = t + ":" + v.attrib["id"]
            self._vardict[vid]['name'] = v.attrib['name']
            self._vardict[vid]["id"] = vid
            self._vardict[vid]["type"] = t

	    n =  v.attrib['name']
            if n in self.name2var :
                warn("Duplicate Var name (0) : (1) (2)".format(n,
                            vid, self.name2var[n]), IsyRuntimeWarning)
            else :
                self.name2var[n] = vid

	    # name2id to replace name2var as a global lookup table
	    if n in self._name2id :
		print("Dup name2id : \"" + n + "\" : " + vid)
		print("\tname2id ", self._name2id[n])
	    else :
		self._name2id[n] = ("var", vid)

    # self._printdict(self._vardict)

##    def set_var_value(self, vname, val, init=0):
#        if self.debug & 0x01 :
#            print("set_var :" + vname)
#
#        varid = self._var_get_id(vname)
#        if varid in self._vardict :
#            self._set_var_value(varid, val, init)
#        else :
#            raise LookupError("var_set_value: unknown var : " + str(var) )
#
#
#    def _set_var_value(self, varid, val, init=0):
#        vid = varid.split(':')
#        if init :
#            xurl = "/rest/vars/init/" + a[0] + "/" + a[1] + "/" + val
#        else :
#            xurl = "/rest/vars/set/" + a[0] + "/" + a[1] + "/" + val
#
#        if self.debug & 0x02 :
#            print("xurl = " + xurl)
#
#        resp = self._getXMLetree(xurl)
#        self._printXML(resp)
#        if resp.attrib["succeeded"] != 'true' :
#            raise IsyResponseError("ISY command error : varid=" +
#                str(varid) + " cmd=" + str(cmd_id))

def var_set_value(self, var, val, prop="val") :
    """ Set var value by name or ID

        args:
            var = var name or Id
            val = new value
            prop = property to addign value to (default = val)

        raise:
            LookupError :  if var name or Id is invalid
            TypeError :  if property is not 'val or 'init'

    """
    if self.debug & 0x04 :
        print("var_set_value ", val, " : ", prop)
    varid = self._var_get_id(var)

    if isinstance(val, str) and  not val.isdigit() :
        raise IsyValueError("var_set_value: value must be an int")
    else :
        val = int(val)

    if val > 2147483647 or val < -2147483648 :
        raise IsyValueError("var_set_value: value larger then a signed int")

    if not varid :
        raise IsyPropertyError("var_set_value: unknown var : " + str(var) )
    if not prop in ['init', 'val'] :
        raise IsyPropertyError("var_set_value: unknown propery : " + str(prop) )
    self._var_set_value(varid, val, prop)

def _var_set_value(self, varid, val, prop="val") :
    """ Set var value by name or ID """
    if self.debug & 0x04 :
        print("_var_set_value ", str(val), " : ", prop)
    a = varid.split(':')
    if prop == "init" :
        xurl = "/rest/vars/init/" + a[0] + "/" + a[1] + "/" + str(val)
    else :
        xurl = "/rest/vars/set/" + a[0] + "/" + a[1] + "/" + str(val)
    if self.debug & 0x02 : print("xurl = " + xurl)
    resp = self._getXMLetree(xurl)

    # pprint.pprint(resp)
    if resp == None or resp.attrib["succeeded"] != 'true' :
        raise IsyResponseError("Var Value Set error : var={!s} prop={!s} val={!s}".format(varid, prop, val))
    if not self.eventupdates and hasattr(self, '_vardict') :
        # self._printdict(self._vardict[varid])
        self._vardict[varid][prop] = int(val)
        # self._printdict(self._vardict[varid])
    return

def var_get_value(self, var, prop="val") :
    """ Get var value by name or ID
        args:
            var = var name or Id
            prop = property to addign value to (default = val)

        raise:
            LookupError :  if var name or Id is invalid
            TypeError :  if property is not 'val or 'init'
    """
    varid = self._var_get_id(var)
    if not varid :
        raise LookupError("var_set_value: unknown var : " + str(var) )
    if not prop in ['init', 'val'] :
        raise TypeError("var_set_value: unknown propery : " + str(prop) )
    if varid in self._vardict :
        return(self._vardict[varid][prop])


# to conform with node and prog API calls
def var_addrs(self) :
    return self.var_ids()


def var_ids(self)  :
    if not self._vardict :
        self.load_vars()

    return self._vardict

def var_names(self)  :
    """ access method for var addresses

        args: None

        returns :  a iist view of var ids
    """
    if not self._vardict :
        self.load_vars()

    return self.name2var.viewkeys()


def get_var(self, vname) :
    """ get var class obj 

        args : var name or Id

        returns : a IsyVar obj

        raise:
            LookupError :  if var name or Id is invalid

    """
    if self.debug & 0x01 :
        print("get_var :" + vname)

    varid = self._var_get_id(vname)
    # print("\tvarid : " + varid)
    if varid in self._vardict :
        if not varid in self.varCdict :
            # print("not varid in self.varCdict:")
            # self._printdict(self._vardict[varid])
            self.varCdict[varid] = IsyVar(self, self._vardict[varid])
        #self._printdict(self._vardict)
        # print("return : ",)
        #self._printdict(self.varCdict[varid])
        return self.varCdict[varid]
    else :
        if self.debug & 0x01 :
            print("Isy get_var no var : \"%s\"" % varid)
        raise LookupError("no var : " + str(varid) )


def _var_get_id(self, vname):
    """ Lookup var value by name or ID
    returns ISY Id  or None
    """
    if not self._vardict :
        self.load_vars()
    
    if isinstance(vname, IsyVar) :
        return vname["id"]
    else :
        v = str(vname)
    if (v).upper() in self._vardict :
        # print("_get_var_id : " + v + " vardict " + v.upper())
        return v.upper()
    if v in self.name2var :
        # print("_var_get_id : " + v + " name2var " + self.name2var[v])
        return self.name2var[v]

    # print("_var_get_id : " + n + " None")
    return None

def var_get_type(self, var) :
    """ Takes Var name or ID and returns type

        arg:
            a var name  ID or Obj

        return
            "Integer" "State" or None
    """
    v = self._var_get_id(var)
    if v in self._vardict :
        vtype, vid = str(v).split(':') 
        if  vtype == "1" :
            return "Integer"
        elif vtype == "2" :
            return "State"
    return "none"


def var_iter(self, vartype=0):
    """ Iterate though vars objects

        args: 
            nodetype : type of var to return

        returns :
            Return an iterator over the Var Obj
    """
    if not self._vardict :
        self.load_vars()

    k = self._vardict.keys()
    for v in k :
        if vartype :
            vartype = str(vartype)
            if self._vardict[v]["type"] == vartype :
                yield self.get_var(v)
        else :
            yield self.get_var(v)

def var_new(self, id=None, varname=None, vartype="int") :
    """ Make new Vara

	Named args:
	    varname	
	    vartype		"integer" or "state"
	
    """
    if varname == None :
	raise IsyValueError("varname : invalid var name")

    if vartype == "integer" :
	varpath="/CONF/INTEGER.VAR"
    elif vartype == "state" :
	varpath="/CONF/STATE.VAR"
    else :
	raise IsyValueError("vartype : invalid type")

    result = self.soapcomm("GetSysConf", name=varpath)

    if result is None  :
	raise IsyResponseError("Error loading Sys Conf file {0}".format(varpath))

    var_et = ET.fromstring(result) 

    # create a dict with all used Ids, then loop till ya find a unused one
    tdict = dict()
    for vdat in var_et.iter("e") :
	tdict[ vdat.attrib['id'] ] = 1
    maxid = tdict.__len__() + 5
    newid = -1
    for i in range(1, maxid) :
	if str(i) not in tdict :
	    newid = str(i)
	    break
    else :
	raise RuntimeError( "failed to find free var id")
    del tdict

    # now that we have a avalible ID number, create the entery
    ET.SubElement(var_et, "e", {'id':newid, 'name':varname} )

    new_var_data =  ET.tostring(var_et)
    #if self.debug == 0x200 :

    print "new_var_data = ", new_var_data

    r = self._sendfile(data=new_var_data, filename=varpath, load="y")
    return r


def _var_delete(self, varid=None, vartype=None) :
    """
	Delete Vara

	Named args:
	    varname	
	    vartype		"integer" or "state"
    """

    if varid is None :
	raise IsyValueError("varid arg in missing")
    elif isinstance(varid, int) :
	varid=str(varid)

#    if isinstance(varid, str) and not val.isdigit() ) :
#	raise IsyValueError("Invalid var id missing")


    if vartype == "integer" :
	varpath="/CONF/INTEGER.VAR"
    elif vartype == "state" :
	varpath="/CONF/STATE.VAR"
    else :
	raise IsyValueError("vartype : invalid type")

    result = self.soapcomm("GetSysConf", name=varpath)

    if result is None  :
	raise IsyResponseError("Error loading Sys Conf file {0}".format(varpath))

    var_et = ET.fromstring(result) 
    for v in var_et.iter("e") :
	if "id" in v.attrib :
	    if v.attrib["id"] == varid :
		var_et.remove(v)
		break
    else :
	warn("Var ID {0} not found".format(varid), IsyRuntimeWarning, 2)
	return None

    new_var_data =  ET.tostring(var_et)

    r = self._sendfile(data=new_var_data, filename=varpath, load="y")
    return r



# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
