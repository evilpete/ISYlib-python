from urllib2 import URLError

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"

__all__ = [ 'IsyError', 'IsyNodeError',
	'IsyResponseError', 'IsyPropertyError', 'IsyValueError',
	'IsyInvalidCmdError',
	'IsySoapError', 'IsyTypeError',
	'IsyCommunicationError',
	'IsyRuntimeWarning', 'IsyWarning'
	]

from urllib2 import URLError, HTTPError

#
# The Following was lifted from other modules used as examples
#
class IsyError(Exception):
    """ISY Base exception

SubClasses :
    - IsyResponseError(IsyError):
    - IsyPropertyError(IsyError):
    - IsyValueError(IsyError):
    - IsyInvalidCmdError(IsyError):
    - IsyPropertyValueError(IsyError):
    - IsyAttributeError(IsyError):

    """
    def __init__(self, msg, exception=None, httperr=None):
        """Creates an exception. The message is required, but the exception
        is optional."""
        self._msg = msg
        self._exception = exception
	self.httperr = httperr
	if self.httperr is not None :
	    self.httperrbody = httperr.read()
	else :
	    self.httperrbody = None
        Exception.__init__(self, msg)

    def code(self):
	if self.httperr is not None :
	    return self.httperr.code
	return None

    def getMessage(self):
        "Return a message for this exception."
        return self._msg

    def getException(self):
        "Return the embedded exception, or None if there was none."
        return self._exception

    def __str__(self):
        "Create a string representation of the exception."
        return self._msg

    def __getitem__(self, ix):
        """Avoids weird error messages if someone does exception[ix] by
        mistake, since Exception has __getitem__ defined."""
        raise AttributeError("__getitem__({0})".format(ix))


class IsyCommunicationError(IsyError, URLError):
    """Failed Server connection of responce ."""
    pass

# class IsyCommandError(IsyError):
#     """General exception for command errors."""
#     pass

class IsySoapError(IsyError, HTTPError):
    """General exception for SOAP errors."""
#    def __init__(self, message, Errors):
#
#	# Call the base class constructor with the parameters it needs
#	HTTPError.__init__(self, message)
#
#	# Now for your custom code...
#	self.Errors = Errors
    

    pass

class IsyTypeError(IsyError, TypeError):
    """General exception for Type errors."""
    pass

class IsyNodeError(IsyError):
    """General exception for Node errors."""
    pass

class IsyResponseError(IsyError, RuntimeError):
    """General exception for Isy responce errors."""
    pass

class IsyLookupError(IsyError, LookupError):
    """General exception for property errors."""
    pass

class IsyPropertyError(IsyError, LookupError):
    """General exception for property errors."""
    pass

class IsyInternalError(IsyError):
    """General exception for Internal errors."""
    pass

class IsyValueError(IsyError, ValueError):
    """General exception for arg value errors."""
    pass

# IsyInvalidValueError ??
class IsyInvalidArgError(IsyError):
    """General exception for command errors."""
    pass

class IsyInvalidCmdError(IsyError):
    """General exception for command errors."""
    pass

#class IsyPropertyValueError(IsyError):
#    """General exception for Isy errors."""
#    pass

class IsyAttributeError(IsyError, AttributeError):
    """General exception for Isy errors."""
    pass


class IsyWarning(Warning) :
    pass

class IsyRuntimeWarning(IsyWarning, RuntimeWarning) :
    pass


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
