Help on package ISY:

NAME
    ISY

FILE
    /usr/home/shipley/Projects/ISYlib-python/ISY/__init__.py

PACKAGE CONTENTS
    IsyClass
    IsyDiscover
    IsyEvent
    IsyEventData
    IsyExceptionClass
    IsyNodeClass
    IsyProgramClass
    IsySoap
    IsyUtilClass
    IsyVarClass
    _isyclimate
    _isynode
    _isyprog
    _isyvar
    _isywol

CLASSES
    ISY.IsyNodeClass._IsyNodeBase(ISY.IsyUtilClass.IsySubClass)
        ISY.IsyNodeClass.IsyNode
    ISY.IsyUtilClass.IsySubClass(ISY.IsyUtilClass.IsyUtil)
        ISY.IsyVarClass.IsyVar
    ISY.IsyUtilClass.IsyUtil(__builtin__.object)
        ISY.IsyClass.Isy
    
    class Isy(ISY.IsyUtilClass.IsyUtil)
     |  Obj class the represents the ISY device
     |  
     |  Keyword Args :
     |      addr :      IP address of ISY
     |      userl/userp : User Login / Password
     |  
     |      debug :     Debug flags (default 0)
     |      cachetime : cache experation time [NOT USED] (default 0)
     |      faststart : ( ignored if eventupdate is used )
     |              0=preload cache as startup
     |              1=load cache on demand
     |      eventupdates: run a sub-thread and stream  events updates from ISY
     |                  same effect as calling  Isy().start_event_thread()
     |  
     |  Method resolution order:
     |      Isy
     |      ISY.IsyUtilClass.IsyUtil
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __del__(self)
     |  
     |  __delitem__(self, nodeaddr)
     |  
     |  __getitem__(self, nodeaddr)
     |      access node obj line a dictionary entery
     |  
     |  __init__(self, userl='admin', userp='admin', **kwargs)
     |  
     |  __iter__(self)
     |      iterate though Node Obj (see: node_iter() )
     |  
     |  __repr__(self)
     |  
     |  __setitem__(self, nodeaddr, val)
     |      This allows you to set the status of a Node by
     |      addressing it as dictionary entery
     |  
     |  batch(self, on=-1)
     |  
     |  batterypoweredwrites(self, on=-1)
     |      #/rest/batterypoweredwrites
     |  
     |  clim_get_val(self, prop)
     |  
     |  clim_iter(self)
     |      Iterate though climate values
     |      
     |      args:  
     |          None
     |      
     |      returns :
     |          Return an iterator over the climate values
     |  
     |  clim_query(self)
     |      returns dictionary of climate info
     |  
     |  get_node(self, node_id)
     |      Get a Node object for given node or scene name or ID
     |      
     |      args:
     |          node : node name of id
     |      
     |      return:
     |          An IsyNode object representing the requested Scene or Node
     |  
     |  get_prog(self, pname)
     |      get prog class obj
     |  
     |  get_var(self, vname)
     |      get var class obj 
     |      
     |      args : var name or Id
     |      
     |      returns : a IsyVar obj
     |      
     |      raise:
     |          LookupError :  if var name or Id is invalid
     |  
     |  load_clim(self)
     |      Load climate data from ISY device
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_conf(self)
     |      Load configuration of the system with permissible commands 
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_log_id(self)
     |  
     |  load_log_type(self)
     |      ##
     |      ## Logs
     |      ##
     |  
     |  load_node_types(self)
     |      Load node type info into a multi dimentional dictionary
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_nodes(self)
     |      Load node list scene list and folder info
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_prog(self)
     |      Load Program status and Info
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_vars(self)
     |      Load variable names and values
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  load_wol(self)
     |      Load Wake On LAN IDs 
     |      
     |      args : none
     |      
     |      internal function call
     |  
     |  log_format_line(self, line)
     |      format a ISY log line into a more human readable form
     |  
     |  log_iter(self, error=0)
     |      iterate though log lines 
     |      
     |      args:  
     |          error : return error logs or now
     |      
     |      returns :
     |          Return an iterator log enteries
     |  
     |  log_query(self, errorlog=0, resetlog=0)
     |      get log from ISY
     |  
     |  log_reset(self, errorlog=0)
     |      clear log lines in ISY
     |  
     |  network(self)
     |  
     |  node_addrs(self)
     |      access method for node addresses
     |      returns a iist scene/group addresses
     |  
     |  node_comm(self, naddr, cmd, *args)
     |      send command to a node or scene
     |  
     |  node_get_prop(self, naddr, prop)
     |      # [Needs fixing]
     |      #
     |      # Get property for a node
     |  
     |  node_get_type(self, typid)
     |      Take a node's type value and returns a string idnentifying the device
     |  
     |  node_iter(self, nodetype='')
     |      Iterate though nodes
     |      
     |      args: 
     |          nodetype : type of node to return
     |      
     |      returns :
     |          Return an iterator over the Node Obj
     |  
     |  node_names(self)
     |      access method for node names
     |      returns a dict of ( Node names : Node address )
     |  
     |  node_set_prop(self, naddr, prop, val)
     |      calls /rest/nodes/<node-id>/set/<property>/<value>
     |  
     |  prog_comm(self, paddr, cmd)
     |  
     |  prog_iter(self)
     |      Iterate though program objects
     |      
     |      Returns an iterator over Program Objects types
     |  
     |  scene_addrs(self)
     |      access method for scene addresses
     |      returns a iist scene/group addresses
     |  
     |  scene_names(self)
     |      access method for scene names
     |      returns a dict of ( Node names : Node address )
     |  
     |  start_event_thread(self, mask=0)
     |      starts event stream update thread
     |  
     |  stop_event_tread(self)
     |      Stop update thread
     |  
     |  subscriptions(self)
     |  
     |  sys(self)
     |  
     |  time(self)
     |  
     |  var_addrs(self)
     |      access method for var addresses
     |      
     |      args: None
     |      
     |      returns :  a iist view of var ids
     |  
     |  var_get_type(self, var)
     |      Takes Var name or ID and returns type
     |      
     |      arg:
     |          a var name  ID or Obj
     |      
     |      return
     |          "Integer" "State" or None
     |  
     |  var_get_value(self, var, prop='val')
     |      Get var value by name or ID
     |      args:
     |          var = var name or Id
     |          prop = property to addign value to (default = val)
     |      
     |      raise:
     |          LookupError :  if var name or Id is invalid
     |          TypeError :  if property is not 'val or 'init'
     |  
     |  var_iter(self, vartype=0)
     |      Iterate though vars objects
     |      
     |      args: 
     |          nodetype : type of var to return
     |      
     |      returns :
     |          Return an iterator over the Var Obj
     |  
     |  var_set_value(self, var, val, prop='val')
     |      Set var value by name or ID
     |      
     |      args:
     |          var = var name or Id
     |          val = new value
     |          prop = property to addign value to (default = val)
     |      
     |      raise:
     |          LookupError :  if var name or Id is invalid
     |          TypeError :  if property is not 'val or 'init'
     |  
     |  wol(self, wid)
     |      Send Wake On LAN to registared wol ID
     |  
     |  wol_iter()
     |      Iterate though Wol Ids values
     |  
     |  wol_names(self)
     |      method to retrieve a list of WOL names
     |      returns List of WOL names and IDs or None
     |  
     |  x10_comm(self, unit, cmd)
     |      direct send x10 command
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  app_version
     |      name of ISY app_version (readonly)
     |  
     |  platform
     |      name of ISY platform (readonly)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class IsyNode(_IsyNodeBase)
     |  Node Class for ISY
     |  
     |  Attributes :
     |      status / ST
     |      ramprate / RR
     |      onlevel / OL
     |  
     |  Readonly Attributes :
     |      address
     |      formatted
     |      enabled
     |      pnode
     |      type
     |      name
     |      ELK_ID
     |      flag
     |  
     |  funtions:
     |      get_rr:
     |      set_rr:
     |  
     |  Method resolution order:
     |      IsyNode
     |      _IsyNodeBase
     |      ISY.IsyUtilClass.IsySubClass
     |      ISY.IsyUtilClass.IsyUtil
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __bool__(self)
     |      # experimental
     |  
     |  __float__(self)
     |  
     |  __hash__(self)
     |      # use the node address as the hash value
     |  
     |  __init__(self, isy, ndict)
     |  
     |  get_ol(self)
     |      Get/Set On Level property of Node
     |  
     |  get_rr(self)
     |      Get/Set RampRate property of Node
     |  
     |  get_status(self)
     |      Get/Set Status property of Node
     |  
     |  set_ol(self, new_value)
     |      Get/Set On Level property of Node
     |  
     |  set_rr(self, new_value)
     |      Get/Set RampRate property of Node
     |  
     |  set_status(self, new_value)
     |      Get/Set Status property of Node
     |  
     |  update(self)
     |      force object to manualy update it's propertys
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  onlevel
     |      Get/Set On Level property of Node
     |  
     |  ramprate
     |      Get/Set RampRate property of Node
     |  
     |  status
     |      Get/Set Status property of Node
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from _IsyNodeBase:
     |  
     |  __contains__(self, other)
     |      # check if scene _contains_ node
     |  
     |  beep(self)
     |  
     |  is_member(self, obj)
     |  
     |  member_iter(self)
     |  
     |  member_list(self)
     |  
     |  off(self)
     |      Send Off command to a node
     |      
     |      args: None
     |  
     |  on(self, val=255)
     |      Send On command to a node
     |      
     |      args: 
     |          take optional value for on level
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from ISY.IsyUtilClass.IsySubClass:
     |  
     |  __delitem__(self, prop)
     |  
     |  __eq__(self, other)
     |      # This allows for
     |  
     |  __getattr__(self, attr)
     |  
     |  __getitem__(self, prop)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed in  a dict style
     |  
     |  __iter__(self)
     |      Internal method 
     |      
     |      allows Objects properties to be access through iteration
     |  
     |  __repr__(self)
     |  
     |  __setitem__(self, prop)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed/set in a dict style
     |  
     |  get_prop_list(self, l)
     |      Get a list of properties
     |      
     |      args:
     |          prop_list : a list of property names
     |      
     |      returns
     |          a list of property values
     |      
     |      if I property does not exist a value of None is used instead
     |      of raising a Attribute error
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ISY.IsyUtilClass.IsySubClass:
     |  
     |  address
     |      Address or ID of Node (readonly)
     |  
     |  name
     |      Name of Node (readonly)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class IsyVar(ISY.IsyUtilClass.IsySubClass)
     |  VAR Class for ISY
     |  
     |  attributes/properties :
     |      ts :        timetamp
     |      type :      Var Type
     |      init :      inital value for Var ( at ISY boot )
     |      value :     current value
     |      id :        unique for Var used by ISY
     |      name :      name of var
     |  
     |  funtions:
     |      get_var_ts() :      get timestamp
     |      get_var_type() :    get Var type
     |      get_var_init() :    get  inital value for Var
     |      set_var_init(new_value) :   set inital value for Var
     |      get_var_value() :   get current value
     |      set_var_value(new_value) :  set new value for Var
     |      get_var_id() :      get unique for Var used by ISY
     |      get_var_name() :    get name of var
     |  
     |  Method resolution order:
     |      IsyVar
     |      ISY.IsyUtilClass.IsySubClass
     |      ISY.IsyUtilClass.IsyUtil
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __abs__(self)
     |  
     |  __add__(self, n)
     |  
     |  __and__(self, n)
     |      # logic opts
     |  
     |  __bool__(self)
     |  
     |  __cmp__(self, n)
     |  
     |  __div__ = __truediv__(self, n)
     |  
     |  __eq__(self, n)
     |  
     |  __float__(self)
     |  
     |  __floordiv__(self, n)
     |  
     |  __ge__(self, n)
     |  
     |  __gt__(self, n)
     |  
     |  __iadd__(self, n)
     |  
     |  __iand__(self, n)
     |  
     |  __idiv__ = __itruediv__(self, n)
     |  
     |  __ifloordiv__(self, n)
     |  
     |  __ilshift__(self, n)
     |  
     |  __imod__(self, n)
     |  
     |  __imul__(self, n)
     |  
     |  __int__(self)
     |  
     |  __invert__(self)
     |  
     |  __ior__(self, n)
     |  
     |  __ipow__(self, n)
     |  
     |  __irshift__(self, n)
     |  
     |  __isub__(self, n)
     |  
     |  __itruediv__(self, n)
     |  
     |  __ixor__(self, n)
     |  
     |  __le__(self, n)
     |  
     |  __long__(self)
     |  
     |  __lt__(self, n)
     |  
     |  __mul__(self, n)
     |      # Mult &  div
     |  
     |  __ne__(self, n)
     |  
     |  __neg__(self)
     |  
     |  __or__(self, n)
     |  
     |  __radd__ = __add__(self, n)
     |  
     |  __repr__(self)
     |  
     |  __rmul__ = __mul__(self, n)
     |  
     |  __ror__ = __or__(self, n)
     |  
     |  __str__(self)
     |      # Type conversion
     |  
     |  __sub__(self, n)
     |  
     |  __truediv__(self, n)
     |  
     |  __xor__(self, n)
     |  
     |  bit_length(self)
     |  
     |  get_var_init(self)
     |      returns var init value
     |      this is also avalible via the property : init
     |  
     |  get_var_value(self)
     |      returns var value
     |      this is also avalible via the property : value
     |  
     |  set_var_init(self, new_value)
     |      sets var init value
     |      this can also be set via the property : init
     |  
     |  set_var_value(self, new_value)
     |      sets var value
     |      this can also be set via the property : value
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  init
     |      returns var init value
     |      this is also avalible via the property : init
     |  
     |  value
     |      returns var value
     |      this is also avalible via the property : value
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from ISY.IsyUtilClass.IsySubClass:
     |  
     |  __delitem__(self, prop)
     |  
     |  __getattr__(self, attr)
     |  
     |  __getitem__(self, prop)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed in  a dict style
     |  
     |  __init__(self, isy, objdict)
     |      INIT
     |  
     |  __iter__(self)
     |      Internal method 
     |      
     |      allows Objects properties to be access through iteration
     |  
     |  __setitem__(self, prop)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed/set in a dict style
     |  
     |  get_prop_list(self, l)
     |      Get a list of properties
     |      
     |      args:
     |          prop_list : a list of property names
     |      
     |      returns
     |          a list of property values
     |      
     |      if I property does not exist a value of None is used instead
     |      of raising a Attribute error
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ISY.IsyUtilClass.IsySubClass:
     |  
     |  address
     |      Address or ID of Node (readonly)
     |  
     |  name
     |      Name of Node (readonly)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    isy_discover(**kwargs)
        discover a device's IP
        
        named args:
            node : node name of id
            timeout : how long to wait for replies
            count : number of devices to wait for
            passively : passivly wait for broadcast
            debug : print debug info
        
        return: a list of dict obj containing :
                - friendlyName: the device name
                - URLBase: base URL for device
                - UDN: uuid
            ( optional : eventSubURL controlURL SCPDURL  )

DATA
    __all__ = ['Isy', 'IsyUtil', 'IsyUtilClass', 'IsyClass', 'IsyNode', 'I...
    __author__ = 'Peter Shipley <peter.shipley@gmail.com>'
    __revision__ = '$Id$'
    __version__ = '0.1.20130331'

VERSION
    0.1.20130331

AUTHOR
    Peter Shipley <peter.shipley@gmail.com>


