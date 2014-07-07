"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"


from ISY.IsyVarClass import IsyVar
from ISY.IsyExceptionClass import IsyError, IsyInternalError, IsyValueError, \
                            IsyResponseError, IsyPropertyError, \
			    IsyLookupError, \
                            IsyRuntimeWarning, IsyWarning

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
    if self.debug & 0x01 :
        print("load_vars")
    if not hasattr(self, '_vardict') or not isinstance(self._vardict, dict):
        self._vardict = dict()

    if not hasattr(self, '_name2id') or not isinstance(self._name2id, dict):
        self._name2id = dict()

    self.name2var = dict()
    for t in ['1', '2'] :
        vinfo = self._getXMLetree("/rest/vars/get/" + t)
        for v in vinfo.iter("var") :

	    vid = t + ":" + v.attrib["id"]
	    if vid in self._vardict :
		vdat = self._vardict[vid]
	    else :
		vdat = dict()
		self._vardict[vid] = vdat

            for vd in list(v) :
                if vd.tag != "var" :
                    vdat[vd.tag] = vd.text
            vdat["val"] = int(vdat["val"])
            vdat["init"] = int(vdat["init"])
        # self._printdict(self._vardict)

        vinfo = self._getXMLetree("/rest/vars/definitions/" + t)

	# can return None if there are not vars
	if vinfo is None :
	    return

        for v in vinfo.iter("e") :
            # self._printinfo(v, "e :")
            vid = t + ":" + v.attrib["id"]
            self._vardict[vid]['name'] = v.attrib['name']
            self._vardict[vid]["id"] = vid
            self._vardict[vid]["type"] = t

            n = v.attrib['name']
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
#            raise IsyLookupError("var_set_value: unknown var : " + str(var) )
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


def var_refresh_value(self, var) :
    if self.debug & 0x04 :
        print("var_refresh_value : ", var)

    if var is None :
	self.load_vars()
	return

    varid = self._var_get_id(var)

    if not varid :
        raise IsyPropertyError("var_refresh: unknown var : " + str(var))

    a = varid.split(':')
    xurl = "/rest/vars/get/" + a[0] + "/" + a[1]
    resp = self._getXMLetree(xurl)
    print "resp", resp

    if resp is None :
        raise IsyPropertyError("var_refresh: error geting var : " + str(var))

    for vd in list(resp) :
	if vd.tag in self._vardict[varid] :
	    self._vardict[varid][vd.tag] = vd,text

    self._vardict[varid]["val"] = int(self._vardict[varid]["val"])
    self._vardict[varid]["init"] = int(self._vardict[varid]["init"])

    return None



def _var_refresh_value(self, var) :
    pass

def var_set_value(self, var, val, prop="val") :
    """ Set var value by name or ID

        args:
            var                 var name or Id
            val                 new value
            prop                init | val (default = val)

        raise:
            IsyLookupError :  if var name or Id is invalid
            TypeError :  if property is not 'val or 'init'

        max values are a signed 32bit int ( -214748364 to 2147483647 )
    """
    if self.debug & 0x04 :
        print("var_set_value ", val, " : ", prop)

    varid = self._var_get_id(var)

    if isinstance(val, str) and not val.isdigit() :
        raise IsyValueError("var_set_value: value must be an int")
    else :
        val = int(val)

    if val > 2147483647 or val < -2147483648 :
        raise IsyValueError("var_set_value: value larger then a signed int")

    if not varid :
        raise IsyPropertyError("var_set_value: unknown var : " + str(var))
    if not prop in ['init', 'val'] :
        raise IsyPropertyError("var_set_value: unknown propery : " + str(prop))
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
    if resp is None or resp.attrib["succeeded"] != 'true' :
        raise IsyResponseError("Var Value Set error : var={!s} prop={!s} val={!s}".format(varid, prop, val))

    #
    # hasattr(self, '_vardict') :
    if not self.eventupdates and self._vardict is not None :
        # self._printdict(self._vardict[varid])
        if varid in self._vardict :
            self._vardict[varid][prop] = int(val)
        # self._printdict(self._vardict[varid])
    return


def var_get_value(self, var, prop="val") :
    """ Get var value by name or ID
        args:
            var = var name or Id
            prop = property to addign value to (default = val)

        raise:
            IsyLookupError :  if var name or Id is invalid
            TypeError :  if property is not 'val or 'init'
    """
    varid = self._var_get_id(var)
    if not varid :
        raise IsyLookupError("var_set_value: unknown var : " + str(var))
    if not prop in ['init', 'val'] :
        raise TypeError("var_set_value: unknown propery : " + str(prop))
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
            IsyLookupError :  if var name or Id is invalid

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
        raise IsyLookupError("no var : " + vname + " : " + str(varid))


def _var_get_id(self, vname):
    """ Lookup var value by name or ID
    returns ISY Id or None
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
        if vtype == "1" :
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


def var_new(self, varid=None, varname=None, vartype="int", value=None, initval=None) :
    return self.var_add(varid=varid, varname=varname, vartype=vartype, value=value, initval=initval)


def var_add(self, varid=None, varname=None, vartype="int", value=None, initval=None) :
    """ Adds or replaces a var

            Named args:
                varname
                vartype         "integer" or "state"
                initval         inital value (optional)
                value           current value (optional)

    """
    if varname is None :
        raise IsyValueError("varname : invalid var name")

    if vartype == "integer" :
        varpath = "/CONF/INTEGER.VAR"
        vtype = "1"
    elif vartype == "state" :
        varpath = "/CONF/STATE.VAR"
        vtype = "2"
    else :
        raise IsyValueError("vartype : invalid type")

    if value is not None :
        if isinstance(value, int) :
            value = str(value)
        elif not (isinstance(value, str) and value.isdigit()) :
            raise IsyValueError("var_add: value must be an int or None")


    if initval is not None :
        if isinstance(initval, int) :
            initval = str(initval)
        elif not (isinstance(initval, str) and initval.isdigit()) :
            raise IsyValueError("var_add: initval must be an int None")

    result = self.soapcomm("GetSysConf", name=varpath)

    if result is None  :
        raise IsyResponseError("Error loading Sys Conf file {0}".format(varpath))

    var_et = ET.fromstring(result)

    if varid is None :
        # create a dict with all used Ids, then loop till ya find a unused one
        tdict = dict()
        for vdat in var_et.iter("e") :
            tdict[vdat.attrib['id']] = 1
        maxid = tdict.__len__() + 5
        varid = -1
        for i in range(1, maxid) :
            if str(i) not in tdict :
                varid = str(i)
                break
        else :
            raise RuntimeError("failed to find free var id")
        del tdict
    else :
        if isinstance(varid, int) :
            varid = str(varid)
        elif not (isinstance(varid, str) and varid.isdigit()) :
            raise IsyValueError("var_add: varid must be an int or None")


    vaddr = vtype + ":" + varid

    # now that we have a avalible ID number, create the entery
    ET.SubElement(var_et, "e", {'id': varid, 'name': varname})

    new_var_data = ET.tostring(var_et, method='html')
    print "new_var_data=", new_var_data

    # This is stupid but method='html' lowercases closing tags
    # regardless of the opening tag case.
    new_var_data = new_var_data.replace("</clist>", "</CList>")
    print "new_var_data=", new_var_data

    r = self._sendfile(data=new_var_data, filename=varpath, load="y")

    # update local cache ( if preloaded )
    if self._vardict is not None :
        import time

        if vaddr in self._vardict :
            newv = self._vardict[vaddr]
        else :
            newv = dict()
            self._vardict[vaddr] = newv

        newv['id'] = vaddr
        newv['type'] = vtype
        newv['name'] = varname

        newv['ts'] = time.strftime("%Y%m%d %H:%M:%S", time.localtime()),

        if initval is None :
            newv['init'] = 0
        else :
            newv['init'] = value

        if value is None :
            newv['val'] = 0
        else :
            newv['val'] = value


    # store values ( if given )
    if value is not None :
        val = str(value)
        _var_set_value(self, vaddr, val, prop="val")
    if initval is not None :
        val = str(initval)
        _var_set_value(self, vaddr, val, prop="init")

    return r


def var_delete(self, varid=None) :
    """
        Delete Vara

        arg:
            varid       var name or address id

        note : var delete is not an atomic operation
    """
    if varid is None :
        raise IsyValueError("{0} : varid arg is missing".format(__name__))

    myvarid = self._var_get_id(varid)

    if isinstance(varid, list) :
        for i in range(len(varid)) :  # make sure they are all strings
            if not isinstance(varid[i], str) :
                varid[i] = str(varid[i])
    else :  # if not a list make is a list
        varid = [str(varid)]

    dellist= {"1" : [], "2" :  []}

    for v in varid :
        vtype, vid = v.split(":")
        dellist[vtype].append(vid)

    if dellist["1"]  :
        self._var_delete(dellist["1"], "1")

    if dellist["2"]  :
        self._var_delete(dellist["2"], "2")


def _var_delete(self, varid=None, vartype=None) :
    """
            Named args:
                varid           a var id (or list of ids)
                vartype         "integer" or "state"

        if varid is a list, then all deletions will happen in one operation

        note : var delete is not an atomic operation
    """
    if varid is None :
        raise IsyValueError("varid arg is missing")
    elif isinstance(varid, list) :
        for i in range(len(varid)) :  # make sure they are all strings
            varid[i] = str(varid[i])
    else :  # if not a list make is a list
        varid = [str(varid)]


#    if isinstance(varid, str) and not val.isdigit() ) :
#       raise IsyValueError("Invalid var id missing")


    vartype = str(vartype)
    if vartype == "integer" or vartype == "1" :
        varpath = "/CONF/INTEGER.VAR"
    elif vartype == "state" or vartype == "2" :
        varpath = "/CONF/STATE.VAR"
    else :
        raise IsyValueError("vartype : invalid type")

    result = self.soapcomm("GetSysConf", name=varpath)

    if result is None  :
        raise IsyResponseError("Error loading Sys Conf file {0}".format(varpath))

    var_et = ET.fromstring(result)

#$      varid=str(varid)

    # create a list from the iter(element) to tree can be modified
    for v in list(var_et.iter("e")) :
        if "id" in v.attrib :
            if v.attrib["id"] in varid :
                var_et.remove(v)

    new_var_data = ET.tostring(var_et)

    r = self._sendfile(data=new_var_data, filename=varpath, load="y")

    return r


def var_rename(self, var=None, varname=None) :
    """
            Named args:
                var             var id or var name
                varname         New var name

        note : var rename is not an atomic operation
    """
    if not isinstance(varname, str) :
        raise IsyValueError("varname must me type str")

    varid = self._var_get_id(var)

    if varid is None :
        raise IsyValueError("Invalid var : {0}".format(var))

    v = varid.split(":")

    if len(v) != 2 :
        raise IsyInternalError("Invalid var : {0}".format(var))

    # print "call _var_rename ", len(v), v[0], v[1], varname

    r = self._var_rename(vartype=v[0], varid=v[1], varname=varname)

    if varid in self._vardict :
        self._vardict[varid]['name'] = varname
        self.name2var[varname] = vid

#    if varname in self._name2id :
#       if self._name2id[varname][0] == "var" :
#           self._name2id[varname] = ("var", varid)

    return r


def _var_rename(self, vartype=None, varid=None, varname=None) :
    """
            Named args:
                varid           a var id
                vartype         "integer" or "state"
                varname         New var name

        note : not an atomic operation
    """
    if varid is None :
        raise IsyValueError("varid arg is missing")

    elif not isinstance(varid, str) :
        varid = str(varid)


#    if isinstance(varid, str) and not val.isdigit() ) :
#       raise IsyValueError("Invalid var id missing")


    vartype = str(vartype)
    if vartype == "integer" or vartype == "1" :
        varpath = "/CONF/INTEGER.VAR"
    elif vartype == "state" or vartype == "2" :
        varpath = "/CONF/STATE.VAR"
    else :
        raise IsyValueError("vartype : invalid type")

    result = self.soapcomm("GetSysConf", name=varpath)

    if result is None  :
        raise IsyResponseError("Error loading Sys Conf file {0}".format(varpath))

    var_et = ET.fromstring(result)

    for v in var_et.iter("e") :
        if "id" in v.attrib :
            if v.attrib["id"] == varid :
                v.attrib["name"] = varname
                break

    new_var_data = ET.tostring(var_et)

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
