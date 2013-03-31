from IsyUtilClass import *
from IsyClass import *
#from IsyNodeClass import *
# from IsyVarClass import *
 


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
	    get_prog_ts() :	get timestamp
	    get_prog_type() :	get Var type
	    get_prog_init() :	get  inital value for Var
	    set_prog_init(new_value) :	set inital value for Var
	    get_prog_value() :	get current value
	    set_prog_value(new_value) :	set new value for Var
	    get_prog_id() :	get unique for Var used by ISY
	    get_prog_name() :	get name of var

    """
    _getlist = ['enabled', 'folder', 'id', 'lastFinishTime',
	'lastRunTime', 'name', 'nextScheduledRunTime', 'parentId',
	'runAtStartup', 'running', 'status']
    _setlist = [ 'enabled' ]
    _propalias = { 'val':  'status', 'value': 'status',
	    'addr': 'id', 'address': 'id' }


#    def get_prog_enabled(self):
#	return self._get_prop("enabled")
#    enabled = property(get_prog_enabled)

#    def get_prog_folder(self):
#	return self._get_prop("folder")
#    folder = property(get_prog_folder)

#    def get_prog_id(self):
#	return self._get_prop("id")
#    type = property(get_prog_id)

#    def get_prog_lastFinishTime(self):
#	return self._get_prop("lastFinishTime")
#    lastFinishTime = property(get_prog_lastFinishTime)

#    def get_prog_lastRunTime(self):
#	return self._get_prop("lastRunTime")
#    lastRunTime = property(get_prog_lastRunTime)

#    def get_prog_name(self):
#	return self._get_prop("name")
#    name = property(get_prog_name)

#    def get_prog_nextScheduledRunTime(self):
#	return self._get_prop("nextScheduledRunTime")
#    nextScheduledRunTime = property(get_prog_nextScheduledRunTime)

#    def get_prog_parentId(self):
#	return self._get_prop("parentId")
#    parentId = property(get_prog_parentId)

#    def get_prog_runAtStartup(self):
#	return self._get_prop("runAtStartup")
#    runAtStartup = property(get_prog_runAtStartup)

#    def get_prog_running(self):
#	return self._get_prop("running")
#    running = property(get_prog_running)

#    def get_prog_status(self):
#	return self._get_prop("status")
#    status = property(get_prog_status)

    def send_command(self, cmd):
	self.prog_comm(self._mydict['id'], cmd)

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
