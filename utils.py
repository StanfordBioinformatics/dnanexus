import subprocess

import dxpy

import gbsc/gbsc_dnanexus #environment module gbsc/gbsc_dnanexus/current

CONF_FILE = gbsc_dnanexus.CONF_FILE
JSON_CONF = gbsc_dnanexus.JSON_CONF

class UnknownDNAnexusUsername(Exception):
	pass

class InvalidAuthToken(Exception):
	pass

def validate_username(dnanexus_username,exception=False):
	"""
	Function : Checks to see if the supplied username appears in the dnanexus_conf.json configuration file and has an authentication token associated with it.
  Args     : dnanexus_username - str. The DNAnexus login name.
						 exception - bool. When set to true, a gbsc_dnanexus.utils.UnknownDNAnexusUsername() will be raised if 'dnanexus_username' doesn't appear in dnanexus_conf.json. 
												 gbsc_dnanexus.utils.InvalidAuthToken() will be instead raised if 'dnanexus_username' does appear in dnanexus_conf.json, but there isn't an 
												 associated API token. If 'exception' is set to False, then False will be returned rather than raising either of these exceptions.
	Returns  : bool.
	Raises   : If 'exception' is set to True, a gbsc_dnanexus.utils.UnknownDNAnexusUsername() exception or a gbsc_dnanexus.utils.InvalidAuthToken() exception could be raised.
	"""
	if dnanexus_username.startswith("user-"):
		dnanexus_username = dnanexus_username.split("user-")[1]

	if dnanexus_username not in JSON_CONF:
		if not exception:
			return False
		else:
			raise UnknownDNAnexusUsername("{username} is not recognized. Please make sure that the username is entered into {CONF_FILE}".format(username=dnanexus_username,CONF_FILE=CONF_FILE))
	if not JSON_CONF[dnanexus_username]:
		if not exception:
			return False
		else:
			raise InvalidAuthToken("{username} does exist in {CONF_FILE}, but it doesn't have an authentication token specified.".format(username=dnanexus_username,CONF_FILE=CONF_FILE))
	return True


class Utils:
	def __init__(dx_user_name):
		"""
		Args : dx_user_name - The login name of the DNAnexus user.
		"""
		if dx_user_name.startswith("user-"):
			dx_user_name = dx_user_name.split("user-1")[1]

		validate_username(dx_user_name,exception=True)
		subprocess.check_call("log_into_dnanexus.sh -u {}".format(dx_user_name),shell=True)
		self.dx_user_name = "user-" + dx_user_name

	def invite_user_to_org_projects(org,created_after,access_level):
		"""
		Function :
		Args     : created_after : Date (e.g. 2012-01-01) or integer timestamp after which the project was created (negative number means in the past, or use suffix s, m, h, d, w, M, y)")
							 access_level  : str. One of ["VIEW","UPLOAD","CONTRIBUTE","ADMINISTER"], which specifies the ermission level the new member should have on shared projects.")
															 See https://wiki.dnanexus.com/API-Specification-v1.0.0/Project-Permissions-and-Sharing for details on the different access levels.
		Returns  :
		"""
		if not org.startswith("org-"):
			org = "org-" + org

		projects_invited_to = []
		gen = dxpy.org_find_projects(org_id=org,created_after=created_after)
		for i in gen:
		  current_level = i["level"]
		  if current_level != access_level:
		    project = dxpy.DXProject(i["id"])
		    project.invite(invitee=internal_dx_username,level=level,send_email=False)
		    logger.info("Invited {user} to {project_name} with level {level}.".format(user=internal_dx_username,project_name=project.name,level=level))	
				projects_invited_to.append(project.name)
		return projects_invited_to
	
	
	
	
	
	
	
	
	
	
	
