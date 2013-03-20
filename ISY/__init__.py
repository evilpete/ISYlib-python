

from IsyUtilClass import *
from IsyClass import *
from IsyDiscover import *
#from IsyNodeClass import *
#from IsyVarClass import *
#from IsyProgramClass import *

__version__ = '0.1.20130316'
__author__ = 'Peter Shipley <peter.shipley@gmail.com>'


#__all__ = ['IsyUtil', 'Isy',  'IsyNode', 'IsyProgram', 'IsyVar']
__all__ = ['Isy', 'IsyUtil', 'IsyUtilClass', 'IsyClass',  'IsyNode', 'IsyVar',
	    'isy_discover']
#__all__ = ['IsyUtil', 'Isy']



#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("ISY.py syntax ok")
    exit(0)

