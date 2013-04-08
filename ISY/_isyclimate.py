
##
## Climate funtions
##
def load_clim(self) :
    """ Load climate data from ISY device

	args : none

	internal function call

    """
    if self.debug & 0x01 :
	print("load_clim called")
    clim_tree = self._getXMLetree("/rest/climate")
    self.climateinfo = dict ()
    if clim_tree == None :
	return 
    # Isy._printXML(self.climateinfo)

    for cl in clim_tree.iter("climate") :
	for k, v in cl.items() :
	    self.climateinfo[k] = v
	for ce in list(cl):
	    self.climateinfo[ce.tag] = ce.text

    self.climateinfo["time"] = time.gmtime()

def clim_get_val(self, prop):
    pass

def clim_query(self):
    """ returns dictionary of climate info """
    try:
	self.climateinfo
    except AttributeError:
	self.load_clim()

    #
    # ADD CODE to check self.cachetime
    #
    return self.climateinfo

def clim_iter(self):
    """ Iterate though climate values

	args:  
	    None

	returns :
	    Return an iterator over the climate values
    """
    try:
	self.climateinfo
    except AttributeError:
	self.load_clim()
    k = self.climateinfo.keys()
    for p in k :
	yield self.climateinfo[p]

