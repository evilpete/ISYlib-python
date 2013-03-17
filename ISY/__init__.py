

from IsyUtilClass import *
from IsyClass import *
from IsyNodeClass import *
from IsyVarClass import *
#from IsyProgramClass import IsyProgram
#from IsyVarClass import IsyVar

version = '0.1.20130316'

#__all__ = ['IsyUtil', 'Isy',  'IsyNode', 'IsyProgram', 'IsyVar']
__all__ = ['IsyUtil', 'IsyUtilClass', 'Isy', 'IsyClass',  'IsyNode', 'IsyVar']
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

