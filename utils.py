import gbsc/gbsc_dnanexus #environment module gbsc/gbsc_dnanexus/current

CONF_FILE = gbsc_dnanexus.CONF_FILE
JSON_CONF = gbsc_dnanexus.JSON_CONF

class UnknownDNAnexusUsername(Exception):
	pass

def validate_username(dnanexus_username,exception=False):
	"""
	Function : Checks to see if the supplied username is valid.
	Returns  : bool unless 'exception' is set to True, in which case a dnanexus_seqresults.seqresults.UnknownDNAnexusUsername exception is raised with a useful error message.
	"""
	if dnanexus_username not in JSON_CONF:
		if not exception:
			return False
		else:
			raise UnknownDNAnexusUsername("{username} is not recognized. Please make sure that the username is entered into {conf_file}".format(username=dnanexus_username,conf_file=CONF_FILE))
	return True
	











