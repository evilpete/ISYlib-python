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
        bin/isy_nodespy     - List registered devices
        bin/isy_log.py      - Get event or error logs
        bin/isy_showevents.py - print live stream of events from ISY
        bin/isy_var.py      - Set, Get or display system vars
        bin/isy_progs.py    - List/Run registered programs
        bin/isy_nestset.py  - sync values from a Nest thermostat with an ISY
        bin/isy_net_res.py  - call registered net resorces on ISY
        bin/isy_net_wol.py  - send WOL to registered devices
    
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
    IsyUtilClass
    IsyVarClass
    _isyclimate
    _isynet_resources
    _isynode
    _isyprog
    _isyvar
    _isyzb

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
     |  __init__(self, **kwargs)
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
     |      Batch mode 
     |      
     |          args values:
     |              1 = Turn Batch mode on
     |              0 = Turn Batch mode off
     |              -1 or None = Return Batch mode status
     |      
     |      calls /rest/batteryPoweredWrites/
     |  
     |  batterypoweredwrites(self, on=-1)
     |      Battery Powered Writes
     |      
     |          args values:
     |              1 = Turn Batch mode on
     |              0 = Turn Batch mode off
     |              -1 or None = Return Batch mode status
     |      
     |      returns status of Battery Powered device operations
     |      calls /rest/batteryPoweredWrites/
     |  
     |  callback_del(self, nid)
     |      delete a callback funtion
     |      
     |      args:
     |          node id
     |      
     |      
     |      delete a callback funtion for a Node, if exists.
     |      
     |      no error is raised if callback does not exist
     |  
     |  callback_get(self, nid)
     |      get a callback funtion for a Nodes
     |      
     |          args:
     |              node id
     |      
     |      returns referance to registared callback function for a node
     |      no none exist then value "None" is returned
     |  
     |  callback_set(self, nid, func, *args)
     |      set a callback function for a Node
     |      
     |          args:
     |              node id
     |              referance to a function
     |              * arg list
     |      
     |      Sets up a callback function that will be called whenever there
     |      is a change event for the specified node
     |      
     |      Only one callback per node is supported, If a callback funtion is already
     |      registared for node_id it will be replaced
     |      
     |      requires IsyClass option "eventupdates" to to set
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
     |  electricity(self)
     |      electricity status
     |      
     |          args: none
     |      
     |      Returns electricity module info, "Energy Monitor",
     |      "Open ADR" and "Flex Your Power" status
     |      
     |      Only applicable to 994 Z Series.
     |      
     |      calls: /rest/electricity
     |  
     |  folder_add_node(self, nid, nodeType=1, parent='', parentType=3)
     |      move node/scene from folder 
     |      
     |      Named args:
     |          node
     |          nodeType
     |          parent
     |          parentType
     |      
     |      sets Parent for node/scene 
     |      
     |      calls SOAP SetParent()
     |  
     |  folder_del(self, fid)
     |      delete folder
     |          args: 
     |              fid : folder address, name or Folder Obj
     |      
     |      calls SOAP RemoveFolder()
     |  
     |  folder_del_node(self, nid, nodeType=1)
     |      remove node from folder
     |      
     |      Named args:
     |          node
     |          nodeType
     |      
     |      remove node/scene from folder ( moves to default/main folder )
     |      
     |      calls SOAP SetParent()
     |  
     |  folder_new(self, fid, fname)
     |      create new Folder
     |      
     |          args: 
     |              folder_id = a unique (unused) folder ID
     |              folder name = name for new folder
     |      
     |      
     |      returns error if folder ID is already in use
     |      
     |      calls SOAP AddFolder()
     |  
     |  folder_rename(self, fid, fname)
     |      rename Folder
     |      
     |          args: 
     |              id = folder ID
     |              name = new folder name
     |      
     |      calls SOAP RenameFolder()
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
     |      load log id tables
     |      
     |      **not implemented **
     |  
     |  load_log_type(self)
     |      load log type tables
     |      
     |          args: None
     |      
     |      **not implemented **
     |  
     |  load_net_resource(self)
     |      Load node WOL and  Net Resource config infomation
     |      
     |      args: none
     |  
     |  load_net_wol(self)
     |      Load Wake On LAN networking resources 
     |      
     |      internal function call
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
     |  log_format_line(self, line)
     |      format a ISY log line into a more human readable form
     |      
     |      ** not implemented **
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
     |      args:
     |          errorlog = flag clear error
     |  
     |  net_resource_iter(self)
     |      iterate net_resource data
     |      
     |      args: none
     |  
     |  net_resource_names(self)
     |      method to retrieve a list of networking resource names
     |      
     |          args: none
     |      
     |          returns List of names or None
     |  
     |  net_resource_run(self, rrid)
     |      Calls and executes net resource
     |      
     |          args:
     |              rrid : network resource ID
     |      calls : /rest/networking/resources/<rrid>
     |  
     |  net_wol(self, wid)
     |      Send Wake On LAN to registared wol ID
     |      
     |          args:
     |              wid : WOL resource ID
     |      calls : /rest/networking/wol/<wol_id>
     |  
     |  net_wol_iter(self)
     |      Iterate though Wol Ids values
     |      
     |      args: none
     |  
     |  net_wol_names(self)
     |      method to retrieve a list of WOL names
     |      
     |          args: none
     |      
     |      returns List of WOL names and IDs or None
     |  
     |  network(self)
     |      network configuration
     |      
     |          args: none
     |      
     |      Returns network configuration
     |      calls /rest/network
     |  
     |  node_addrs(self)
     |      access method for node addresses
     |      returns a iist scene/group addresses
     |  
     |  node_comm(self, naddr, cmd, *args)
     |      Send node command 
     |      
     |          args:
     |              naddr = name, address or node obj
     |              cmd = name of command
     |              value = optional value argument for cmd
     |              
     |          raise:
     |              LookupError :  if node name or Id is invalid
     |              IsyPropertyError :  if property invalid
     |              TypeError :  if property valid
     |      
     |      calls /rest/nodes/<node-id>/cmd/<cmd>>/<cmd value>
     |  
     |  node_get_prop(self, naddr, prop_id)
     |      Get node property 
     |      args:
     |          naddr = name, address or node obj
     |          prop_id = name of property
     |      
     |      raise:
     |          LookupError :  if node name or Id is invalid
     |          IsyPropertyError :  if property invalid
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
     |  node_rename(self, nid, nname)
     |      rename Node
     |      
     |          args: 
     |              id = Node ID
     |              name = new Node name
     |      
     |      calls SOAP RenameNode()
     |  
     |  node_set_prop(self, naddr, prop, val)
     |      Set node property 
     |          args:
     |              naddr = name, address or node obj
     |              prop = name of property
     |              val = new value to assign 
     |      
     |          raise:
     |              LookupError :  if node name or Id is invalid
     |              IsyPropertyError :  if property invalid
     |              TypeError :  if property valid
     |      
     |      calls /rest/nodes/<node-id>/set/<property>/<value>
     |  
     |  prog_comm(self, paddr, cmd)
     |      Send program command
     |      
     |          args:
     |              paddr = program name, address or program obj
     |              cmd = name of command
     |              
     |          raise:
     |              LookupError :  if node name or Id is invalid
     |              IsyPropertyError :  if property invalid
     |              TypeError :  if property valid
     |      
     |          Valid Commands : 'run', 'runThen', 'runElse', 'stop', 'enable', 'disable', 'enableRunAtStartup', 'disableRunAtStartup'
     |      
     |      calls  /rest/programs/<pgm-id>/<pgm-cmd>
     |  
     |  prog_iter(self)
     |      Iterate though program objects
     |      
     |      Returns an iterator over Program Objects types
     |  
     |  reboot(self)
     |      Reboot ISY Device
     |          args: none
     |      
     |      calls SOAP Reboot()
     |  
     |  scene_add_node(self, groupid, nid, nflag=16)
     |      add node to Scene/Group
     |      
     |          args: 
     |              group = a unique (unused) scene_id ID
     |              node = id, name or Node Obj
     |              flag = set to 0x10 if node it a controler for Scene/Group
     |      
     |      Add new Node to Scene/Group 
     |      
     |      
     |      calls SOAP MoveNode()
     |  
     |  scene_addrs(self)
     |      access method for scene addresses
     |      returns a iist scene/group addresses
     |  
     |  scene_del(self, sid=None)
     |      delete Scene/Group 
     |      
     |          args: 
     |              id : Scene address, name or Folder Obj
     |      
     |      calls SOAP RemoveGroup()
     |  
     |  scene_del_node(self, groupid, nid)
     |      Remove Node from Scene/Group
     |      
     |          args:
     |              group = address, name or Scene Obj
     |              id = address, name or Node Obj
     |      
     |      calls SOAP RemoveFromGroup()
     |  
     |  scene_names(self)
     |      access method for scene names
     |      returns a dict of ( Node names : Node address )
     |  
     |  scene_new(self, nid=0, sname=None)
     |      new Scene/Group
     |      
     |          args: 
     |              id = a unique (unused) Group ID
     |              name = name for new Scene/Group
     |      
     |      ***No error is given if Scene/Group ID is already in use***
     |      
     |      calls SOAP AddGroup()
     |  
     |  scene_rename(self, fid, fname)
     |      rename Scene/Group
     |      
     |          args: 
     |              id = a Scene/Group id
     |              name = new name 
     |      
     |      
     |      calls SOAP RenameGroup()
     |  
     |  start_event_thread(self, mask=0)
     |      starts event stream update thread
     |      
     |      mask will eventually be used to "masking" events
     |  
     |  stop_event_tread(self)
     |      Stop update thread
     |  
     |  subscriptions(self)
     |      get event subscriptions list and states
     |      
     |          args: none
     |      
     |      Returns the state of subscriptions
     |      
     |      calls : /rest/subscriptions
     |  
     |  sys(self)
     |      system configuration
     |      
     |          args: none
     |      
     |      calls : /rest/sys
     |  
     |  time(self)
     |      system time of ISY
     |      
     |          args: none
     |      
     |      calls : /rest/time
     |  
     |  user_dir(self, name='', pattern='')
     |      Get User Folder/Directory Listing
     |      
     |      Named args:
     |          name
     |          pattern
     |      
     |      call SOAP GetUserDirectory()
     |  
     |  user_fsstat(self)
     |      ISY Filesystem Status
     |      
     |      calls SOAP GetFSStat()
     |  
     |  user_getfile(self, name=None)
     |      Get User File
     |      
     |      Named args:
     |          name
     |      
     |      call SOAP GetUserFile()
     |  
     |  user_mkdir(self, name=None)
     |      Make new User Folder/Directory
     |      
     |      Named args:
     |          name
     |      
     |      call SOAP MakeUserDirectory()
     |  
     |  user_mv(self, name=None, newName=None)
     |      Move/Rename User Object (File or Directory)
     |      
     |      Named args:
     |          oldn
     |          newn
     |      
     |      call SOAP MoveUserObject()
     |  
     |  user_rm(self, name=None)
     |      Remove User File
     |      
     |      Named args:
     |          name
     |      
     |      call SOAP RemoveUserFile()
     |  
     |  user_rmdir(self, name=None)
     |      Remove User Folder/Directory
     |      
     |      Named args:
     |          name
     |      
     |      call SOAP RemoveUserDirectory()
     |  
     |  user_uploadfile(self, srcfile='', name=None, data='')
     |      upload User File
     |      
     |      Named args:
     |          name : name of file after upload
     |          data : date to upload 
     |          srcfile : file containing data to upload
     |      
     |      srcfile is use only if data is not set
     |      if both data & srcfile are not set then
     |      the file "name" is used
     |      
     |      calls /file/upload/...
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
     |  Methods inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  sendfile(self, src=None, filename='', data=None, load='n')
     |      upload file
     |  
     |  soapcomm(self, cmd, **kwargs)
     |      takes a command name and a list of keyword arguments. 
     |      each keyword is converted into a xml element
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
     |  get_enable(self)
     |      get enable/disable status a node
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
     |  rename(self, newname)
     |  
     |  set_enable(self, new_bool)
     |      Set enable status a node
     |      
     |      args:
     |          enable bool
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
     |  enable
     |      enable/disable a node
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
     |  is_dimable(self)
     |  
     |  is_member(self, obj)
     |  
     |  member_add(self, node, flag=0)
     |  
     |  member_iter(self, flag=0)
     |  
     |  member_list(self)
     |  
     |  members_list(self)
     |  
     |  nodeType(self)
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
     |  __del__(self)
     |  
     |  __delitem__(self, prop)
     |  
     |  __eq__(self, other)
     |      smarter test for compairing Obj value
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
     |  __setitem__(self, prop, val)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed/set in a dict style
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
     |  Methods inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  sendfile(self, src=None, filename='', data=None, load='n')
     |      upload file
     |  
     |  soapcomm(self, cmd, **kwargs)
     |      takes a command name and a list of keyword arguments. 
     |      each keyword is converted into a xml element
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
     |      get_var_init() :    get  inital value for Var
     |      set_var_init(new_value) :   set inital value for Var
     |      get_var_value() :   get current value
     |      set_var_value(new_value) :  set new value for Var
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
     |      # mathematical operator
     |  
     |  __add__(self, n)
     |      # mathematical operator
     |  
     |  __and__(self, n)
     |      # logic opts
     |  
     |  __bool__(self)
     |      # Type conversion
     |  
     |  __cmp__(self, n)
     |      #  comparison functions
     |  
     |  __div__ = __truediv__(self, n)
     |  
     |  __eq__(self, n)
     |      #  comparison functions
     |  
     |  __float__(self)
     |      # Type conversion
     |  
     |  __floordiv__(self, n)
     |  
     |  __ge__(self, n)
     |      #  comparison functions
     |  
     |  __gt__(self, n)
     |      #  comparison functions
     |  
     |  __iadd__(self, n)
     |      # mathematical operator
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
     |      # Type conversion
     |  
     |  __invert__(self)
     |  
     |  __ior__(self, n)
     |  
     |  __irshift__(self, n)
     |  
     |  __isub__(self, n)
     |      # mathematical operator
     |  
     |  __itruediv__(self, n)
     |  
     |  __ixor__(self, n)
     |  
     |  __le__(self, n)
     |      #  comparison functions
     |  
     |  __long__(self)
     |      # Type conversion
     |  
     |  __lt__(self, n)
     |      #  comparison functions
     |  
     |  __mul__(self, n)
     |      # mathematical operator
     |  
     |  __ne__(self, n)
     |      #  comparison functions
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
     |      # mathematical operator
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
     |  __del__(self)
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
     |  __setitem__(self, prop, val)
     |      Internal method 
     |      
     |      allows Objects properties to be accessed/set in a dict style
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
     |  Methods inherited from ISY.IsyUtilClass.IsyUtil:
     |  
     |  sendfile(self, src=None, filename='', data=None, load='n')
     |      upload file
     |  
     |  soapcomm(self, cmd, **kwargs)
     |      takes a command name and a list of keyword arguments. 
     |      each keyword is converted into a xml element
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
    IsyGetArg(lineargs)
        takes argv and extracts name/pass/ipaddr options
    
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
    __copyright__ = 'Copyright (C) 2013 Peter Shipley'
    __license__ = 'BSD'
    __revision__ = '$Id: c2e51866b60b2ebe8f258dc10ef6f2b89dac221f $'
    __version__ = '0.1.20130528'

VERSION
    0.1.20130528

AUTHOR
    Peter Shipley <peter.shipley@gmail.com>


