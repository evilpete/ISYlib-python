"""API for the Universal Device's ISY 

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

    ISY/*		- ISY Python lib
    bin/isy_find.py	- Upnp probe for devices on your network
    bin/isy_nodespy	- List registered devices
    bin/isy_log.py	- Get event or error logs
    bin/isy_showevents.py - print live stream of events from ISY
    bin/isy_var.py	- Set, Get or display system vars
    bin/isy_progs.py	- List/Run registered programs
    bin/isy_nestset.py	- sync values from a Nest thermostat with an ISY
    bin/isy_net_res.py	- call registered net resorces on ISY
    bin/isy_net_wol.py	- send WOL to registered devices

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

"""

import sys
if sys.hexversion < 0x20703f0 :
    sys.stderr.write("You need python 2.7 or later to run this script\n")

__revision__ = "$Id$"
__version__ = "0.1.20140704"
__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2014 Peter Shipley"
__license__ = "BSD"

#
# from ISY.IsyUtilClass import IsyUtil
#
from ISY.IsyClass import Isy, IsyGetArg
from ISY.IsyDiscover import isy_discover
from ISY.IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder
from ISY.IsyVarClass import IsyVar
from ISY.IsyProgramClass import IsyProgram
from ISY.IsyExceptionClass import IsyError
from ISY.IsyDebug import *
#





#__all__ = ['IsyUtil', 'Isy',  'IsyNode', 'IsyProgram', 'IsyVar']
__all__ = ['Isy', 'IsyUtil', 'IsyUtilClass', 'IsyClass',  'IsyNode', 'IsyVar',
	    'isy_discover', 'IsyGetArg']
#__all__ = ['IsyUtil', 'Isy']




#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    #print(__main__.__file___)
    print("ISY.__init__")
    print("syntax ok")
    exit(0)

