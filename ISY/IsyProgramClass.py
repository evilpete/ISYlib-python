from IsyUtilClass import *
from IsyClass import *
#from IsyNodeClass import *
# from IsyVarClass import *
 


__all__ = ['IsyProgram']

class IsyProgram(IsyUtil):
    """ Program Class for ISY

	attributes/properties :
	    enabled : 'true',
	    folder : 'false',
	    id : '0002',
	    lastFinishTime : '2013/03/16 13:35:26',
	    lastRunTime : '2013/03/16 13:35:26',
	    name : 'QueryAll',
	    nextScheduledRunTime : '2013/03/17 03:00:00',
	    parentId : '0001',
	    runAtStartup : 'false',
	    running : 'idle',
	    status: 'false'},


	funtions:
	    get_prog_ts() :	get timestamp
	    get_prog_type() :	get Var type
	    get_prog_init() :	get  inital value for Var
	    set_prog_init(new_value) :	set inital value for Var
	    get_prog_value() :	get current value
	    set_prog_value(new_value) :	set new value for Var
	    get_prog_id() :	get unique for Var used by ISY
	    get_prog_name() :	get name of var

    """
    def __init__(self, isy, pdict) :
	""" INIT IsyProgram """

        if isinstance(vdict, dict):
            self._mydict = vdict
        else :
            print "error : class IsyProgram called without vdict"
            raise IsyValueError("IsyProgram: called without vdict")

        if isinstance(isy, IsyUtil):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class IsyProgram called without Isy"
            raise TypeError("IsyProgram: isy is wrong class")

        if self.debug & 0x04 :
	    print "IsyProgram: ",
	    self._printdict(self._mydict)


	self.getlist = ['enabled', 'folder', 'id', 'lastFinishTime',
	    'lastRunTime', 'name', 'nextScheduledRunTime', 'parentId',
	    'runAtStartup', 'running', 'status']
	self.setlist = [ 'enabled' ]
	self.propalias = { }



    def _get_prog_prop(self, prop):
	if prop in self.propalias :    
	    prop = self.propalias[prop]

	if prop in self.getlist : 
	    if prop in self._mydict :
		return(self._mydict[prop])
	return(None)

    def _set_prog_prop(self, prop, val):
	if prop in self.setlist :
	    pass
	else :
            raise IsyPropertyError("_set_prog_prop : "
	    	    "no property Attribute " + prop)


    def get_prog_enabled(self):
	return self._get_prog_prop("enabled")
    enabled = property(get_prog_enabled)


    def get_prog_folder(self):
	return self._get_prog_prop("folder")
    folder = property(get_prog_folder)

    def get_prog_id(self):
	return self._get_prog_prop("id")
    type = property(get_prog_id)

    def get_prog_lastFinishTime(self):
	return self._get_prog_prop("lastFinishTime")
    lastFinishTime = property(get_prog_lastFinishTime)

    def get_prog_lastRunTime(self):
	return self._get_prog_prop("lastRunTime")
    lastRunTime = property(get_prog_lastRunTime)

    def get_prog_name(self):
	return self._get_prog_prop("name")
    name = property(get_prog_name)

    def get_prog_nextScheduledRunTime(self):
	return self._get_prog_prop("nextScheduledRunTime")
    nextScheduledRunTime = property(get_prog_nextScheduledRunTime)

    def get_prog_parentId(self):
	return self._get_prog_prop("parentId")
    parentId = property(get_prog_parentId)

    def get_prog_runAtStartup(self):
	return self._get_prog_prop("runAtStartup")
    runAtStartup = property(get_prog_runAtStartup)

    def get_prog_running(self):
	return self._get_prog_prop("running")
    running = property(get_prog_running)

    def get_prog_status(self):
	return self._get_prog_prop("status")
    status = property(get_prog_status)

    def __getitem__(self, prop):
	return self._get_prog_prop(prop)
	pass

    def __setitem__(self, prop):
	return self._set_prog_prop(prop)
	pass

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )
	pass

    def __get__(self, instance, owner):
	return self._get_prog_prop("status")

    def __set__(self, instance, owner):
	pass

    def __iter__(self):
	for p in self.getlist :
	    if p in self._mydict :
		yield (p , self._mydict[p])
	    else :
		yield (p , None)


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
