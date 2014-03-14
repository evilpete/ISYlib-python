""" Obj Class Isy Program entries """

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"

from ISY.IsyUtilClass import IsySubClass, val2bool
from ISY.IsyClass import  *
#fromm ISY.IsyNodeClass import *
# fromm ISY.IsyVarClass import *

__all__ = ['IsyProgram']

class IsyProgram(IsySubClass):
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
	    get_prog_enable() : 
	    set_prog_enable() : 
	    get_prog_runatstart() :
	    set_prog_runatstart() :
	    send_command() :

            get_prog_ts() :     get timestamp
            get_prog_type() :   get Prog type
            get_prog_init() :   get  inital value for Var
            set_prog_init(new_value) :  set inital value for Var
            get_prog_value() :  get current value
            set_prog_value(new_value) : set new value for Var
            get_prog_id() :     get unique for Var used by ISY
            get_prog_name() :   get name of var

    """
    _getlist = ['enabled', 'folder', 'id', 'lastFinishTime',
        'lastRunTime', 'name', 'nextScheduledRunTime', 'parentId',
        'runAtStartup', 'running', 'status']
    _setlist = [ 'enabled' ]
    _propalias = { 'val':  'status', 'value': 'status',
            'addr': 'id', 'address': 'id' }
    _boollist = [ "enabled", "folder", "status", "runAtStartup"]

    # _objtype = (-1, "program")
    _objtype = "program"

    def _get_prop(self, prop) :
	if prop == 'src' :
	    return self.get_src()
	return super(self.__class__, self)._get_prop(prop)

    def get_prog_enable(self):
	""" check if prog is enabled (bool) """
        #en = self._get_prop("enabled")
	#return bool( en == "true" )
	if "enabled" in self._mydict :
	    return bool( self._mydict["enabled"] == "true" )
	return True 
    def set_prog_enable(self, en):
	rval = val2bool(en)
	#print "set_prog_enable ", rval
	if "enabled" in self._mydict :
	    if rval :
	       self.isy.prog_comm(self._mydict['id'], "enable")
	    else :
	       self.isy.prog_comm(self._mydict['id'], "disable")
	self._mydict["enabled"] = rval
        return rval
    enabled = property(get_prog_enable, set_prog_enable)

    def get_prog_runatstart(self):
	""" check property runAtStartup (bool) """
        #en = self._get_prop("runAtStartup")
	#return bool( en == "true" )
	return bool( self._mydict['runAtStartup'] == "true" )
    def set_prog_runatstart(self, en):
	rval = val2bool(en)
	#print "set_prog_enable ", rval
        if rval :
	   self.isy.prog_comm(self._mydict['id'], "runAtStartup")
        else :
	   self.isy.prog_comm(self._mydict['id'], "disableRunAtStartup")
	self._mydict["runAtStartup"] = rval
        return rval
    runatstart = property(get_prog_runatstart, set_prog_runatstart)

    def get_path(self):
	return self.isy._prog_get_path( self._mydict['id'] )
    path = property(get_path)

    def get_src(self):
	""" get D2D source for program """
	return self.isy.prog_get_src( self._mydict['id'] )
    src = property(get_src)

#    def get_prog_folder(self):
#       return self._get_prop("folder")
#    folder = property(get_prog_folder)

#    def get_prog_id(self):
#       return self._get_prop("id")
#    ptype = property(get_prog_id)

#    def get_prog_lastFinishTime(self):
#       return self._get_prop("lastFinishTime")
#    lastFinishTime = property(get_prog_lastFinishTime)

#    def get_prog_lastRunTime(self):
#       return self._get_prop("lastRunTime")
#    lastRunTime = property(get_prog_lastRunTime)

#    def get_prog_name(self):
#       return self._get_prop("name")
#    name = property(get_prog_name)

#    def get_prog_nextScheduledRunTime(self):
#       return self._get_prop("nextScheduledRunTime")
#    nextScheduledRunTime = property(get_prog_nextScheduledRunTime)

#    def get_prog_parentId(self):
#       return self._get_prop("parentId")
#    parentId = property(get_prog_parentId)

#    def get_prog_runAtStartup(self):
#       return self._get_prop("runAtStartup")
#    runAtStartup = property(get_prog_runAtStartup)

#    def get_prog_running(self):
#       return self._get_prop("running")
#    running = property(get_prog_running)

#    def get_prog_status(self):
#       return self._get_prop("status")
#    status = property(get_prog_status)

    def send_command(self, cmd):
        self.isy.prog_comm(self._mydict['id'], cmd)

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
