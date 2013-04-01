Help on package ISY:

NAME
    ISY - API for the Universal Device's ISY

FILE
    /usr/home/shipley/Projects/ISYlib-python/ISY/__init__.py

DESCRIPTION
    This is a Work in progress
    
    Supporting a Simple and OO interface for ISY home automation netapp
    
    
    see also : http://www.universal-devices.com/residential/
               http://wiki.universal-devices.com/index.php?title=Main_Page
    
    NOTE: This Libaray is not written my or supported by universal devices
    
    
    -----
    
    to use set the following env vars
    
    ISY_ADDR the IP address of your ISY device
    ISY_AUTH your loging and password
    
    eg:
    
        export ISY_AUTH=admin:mypasswd
        export ISY_ADDR=192.168.1.2
    
    Files:
    
        ISY/*               - ISY Python lib
        bin/isy_find.py     - Upnp probe for devices on your network
        bin/isy_list.py     - List registered devices
        bin/isy_log.py      - Get event or error logs
        bin/isy_showevents.py - print live stream of events from ISY
        bin/isy_var.py      - Set, Get or display system vars
    
    The example code included it ment to demonstrate API use with minimal  
    code for clarity.
    
    
    
    This package provides the following classes :
    
    
    
    - Isy - primary class for interacting with a ISY network appliance
        from this class most operations can be made though a simple call interface
    
    - IsyNode - Node Object 
        Represent lights, switches, motion sensors 
    - IsyScene - Scene Object
        Represents Scenes contains Nodes that comprise a "Scene"
    - IsyNodeFolder - Can hold Scene's or Nodes
        a organizational obj for Scene's and Nodes
    - IsyVar -  ISY device Variable 
        Represents a variables that are avalible in the ISY device
    - IsyProgram - ISY device Programs
        Represents a variables that are avalible in the ISY device
    
    
     
    Additional support functions
        - isy_discover - use Upnp to discover IP addr or ISY device
    
    Internal classes 
        - IsyUtil - base class for most ISY classes
        - IsySubClass - base class for sub Objects ( eg: Nodes, Scenes, Vars, Programs )
    
    Exception Classes :
        IsyError
            IsyCommandError
            IsyNodeError
            IsyResponseError
            IsyPropertyError
            IsyValueError
            IsyInvalidCmdError
            IsyPropertyValueError
            IsyAttributeError
    
        UpnpLimitExpired

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

CLASSES
    ISY.IsyUtilClass.IsySubClass(ISY.IsyUtilClass.IsyUtil)
        ISY.IsyNodeClass.IsyNode
        ISY.IsyVarClass.IsyVar
    ISY.IsyUtilClass.IsyUtil(__builtin__.object)
        ISY.IsyClass.Isy
    
    class Isy(ISY.IsyUtilClass.IsyUtil)
     |  Obj class the represents the ISY device
     |  
     |  Method resolution order:
     |      Isy
     |      ISY.IsyUtilClass.IsyUtil
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __delitem__(self, nodeaddr)
     |  
     |  __getitem__(self, nodeaddr)
     |      access a node as dictionary entery
     |  
     |  __init__(self, userl='admin', userp='admin', **kwargs)
     |  
     |  __iter__(self)
     |      iterate though Node Obj
     |      
     |      see : node_iter()
     |  
     |  __setitem__(self, nodeaddr, val)
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
     |  node_addrs(self)
     |      access method for node addresses
     |      returns a iist scene/group addresses
     |  
     |  node_comm(self, naddr, cmd, *args)
     |      send command to a node or scene
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
     |      args:  
     |          None
     |      
     |      returns :
     |          Return an iterator over Program Objects types
     |  
     |  scene_addrs(self)
     |      access method for scene addresses
     |      returns a iist scene/group addresses
     |  
     |  scene_names(self)
     |      access method for scene names
     |      returns a dict of ( Node names : Node address )
     |  
     |  set_var_value(self, vname, val, init=0)
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
     |  var_get_value(self, var, prop='var')
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
     |      args:  
     |          None
     |      
     |      returns :
     |          Return an iterator over the "Wake on Lan" Ids
     |  
     |  wol_names(self, vname)
     |      method to retrieve a list of WOL names
     |      :type wolname: string
     |      :param wolname: the WOL name or ISY Id
     |      :rtype: list
     |      :return: List of WOL names and IDs or None
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
    
    class IsyNode(ISY.IsyUtilClass.IsySubClass)
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
     |      ISY.IsyUtilClass.IsySubClass
     |      ISY.IsyUtilClass.IsyUtil
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __float__(self)
     |  
     |  __init__(self, isy, ndict)
     |  
     |  __nonzero__(self)
     |      # experimental
     |  
     |  get_ol(self)
     |      property On Level Value of Node
     |  
     |  get_rr(self)
     |      Get RampRate property of Node
     |      
     |      args: Nonertype: str
     |      
     |      return: RampRate value
     |  
     |  get_status(self)
     |      property status value of Node
     |  
     |  set_ol(self, new_value)
     |  
     |  set_rr(self, new_value)
     |      set_rr : Get/Set RampRate property of Node
     |  
     |  set_status(self, new_value)
     |  
     |  update(self)
     |      force object to manualy update it's propertys
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  onlevel
     |      property On Level Value of Node
     |  
     |  ramprate
     |      Get RampRate property of Node
     |      
     |      args: Nonertype: str
     |      
     |      return: RampRate value
     |  
     |  status
     |      property status value of Node
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from ISY.IsyUtilClass.IsySubClass:
     |  
     |  __contains__(self, other)
     |      # check if scene _contains_ node
     |  
     |  __delitem__(self, prop)
     |  
     |  __eq__(self, other)
     |      # This allows for
     |  
     |  __get__(self, instance, owner)
     |      Internal method 
     |      
     |      allows Object status to be access as the value of the obj
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
     |  beep(self)
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
     |  on(self, *args)
     |      Send On command to a node
     |      
     |      args: 
     |          take optional value for on level
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
     |  __eq__(self, other)
     |      # This allows for
     |  
     |  __gt__(self, other)
     |  
     |  __int__(self)
     |  
     |  __lt__(self, other)
     |  
     |  __ne__(self, other)
     |  
     |  __nonzero__(self)
     |  
     |  __set__(self, val)
     |      Internal method
     |      
     |      allows Object status to be set as the value of the obj
     |  
     |  __str__(self)
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
     |  __contains__(self, other)
     |      # check if scene _contains_ node
     |  
     |  __delitem__(self, prop)
     |  
     |  __get__(self, instance, owner)
     |      Internal method 
     |      
     |      allows Object status to be access as the value of the obj
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
     |  __repr__(self)
     |  
     |  __setitem__(self, prop)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed/set in a dict style
     |  
     |  beep(self)
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
     |  on(self, *args)
     |      Send On command to a node
     |      
     |      args: 
     |          take optional value for on level
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
        Get a Node object for given node or scene name or ID
        
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


