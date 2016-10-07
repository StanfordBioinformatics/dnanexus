import subprocess

import dxpy

import gbsc_dnanexus #environment module gbsc/gbsc_dnanexus/current

CONF_FILE = gbsc_dnanexus.CONF_FILE
JSON_CONF = gbsc_dnanexus.JSON_CONF

DX_USER_PREFIX = "user-"
DX_ORG_PREFIX = "org-"

class UnknownDNAnexusUsername(Exception):
	pass

class InvalidAuthToken(Exception):
	pass

def strip_dx_userprefix(dx_username):
	if dx_username.startswith(DX_USER_PREFIX):
		dx_username = dx_username.split(DX_USER_PREFIX)[1]
	return dx_username

def add_dx_userprefix(dx_username):
	if not dx_username.startswith(DX_USER_PREFIX):
		dx_username = DX_USER_PREFIX + dx_username
	return dx_username

def strip_dx_orgprefix(org):
	if org.startswith(DX_ORG_PREFIX):
		org = org.split(DX_ORG_PREFIX)[1]
	return org

def add_dx_orgprefix(org):
	if not org.startswith(DX_ORG_PREFIX):
		org = DX_ORG_PREFIX + org
	return org

def validate_billed_to_prefix(billing_account_id,exception=False):
	"""
	Function : Checks whether the billing account ID begins with "user-" in the case of an individual billing accout, or 
						 "org-" in the case of an org billing account."
	Args     : billing_account_id - str. The name of the DNAnexus billing account, specifying either a user billing account or an 
							org billing account.
						 exception - bool. If True, then when the validation fails, a gbsc_utils.utils.InvalidBillingAccountId() exception
							is raised.
	Returns  : True if the validation passes, False if the validation fails and the 'exception' argument is set to False.
	Raises   : gbsc_utils.utils.InvalidBillingAccountId() if the validation fails and the 'exception' argument is set to True.
	"""
	if (not billing_account_id.startswith(DX_USER_PREFIX)) and (not billing_account_id.startswith(DX_ORG_PREFIX)):
		if exception:
			raise InvalidBillingAccountId("Error - {billing_account_id} must start with {DX_USER_PREFIX} if the billing account is for an individual user, or with {DX_ORG_PREFIX} if the billing account is for an org.".format(billing_account_id=billing_account_id,DX_USER_PREFIX=DX_USER_PREFIX,DX_ORG_PREFIX=DX_ORG_PREFIX))
		else:
			return False
	return True

def validate_username(dx_username,exception=False):
	"""
	Function : Checks to see if the supplied username appears in the dnanexus_conf.json configuration file and has an authentication token associated with it.
  Args     : dx_username - str. The DNAnexus login name.
						 exception - bool. When set to true, a gbsc_dnanexus.utils.UnknownDNAnexusUsername() will be raised if 'dx_username' doesn't appear in dnanexus_conf.json. 
												 gbsc_dnanexus.utils.InvalidAuthToken() will be instead raised if 'dx_username' does appear in dnanexus_conf.json, but there isn't an 
												 associated API token. If 'exception' is set to False, then False will be returned rather than raising either of these exceptions.
	Returns  : bool.
	Raises   : If 'exception' is set to True, a gbsc_dnanexus.utils.UnknownDNAnexusUsername() exception or a gbsc_dnanexus.utils.InvalidAuthToken() exception could be raised.
	"""
	dx_username = strip_dx_userprefix(dx_username)
	if dx_username not in JSON_CONF:
		if not exception:
			return False
		else:
			raise UnknownDNAnexusUsername("{username} is not recognized. Please make sure that the username is entered into {CONF_FILE}".format(username=dx_username,CONF_FILE=CONF_FILE))
	if not JSON_CONF[dx_username]:
		if not exception:
			return False
		else:
			raise InvalidAuthToken("{username} does exist in {CONF_FILE}, but it doesn't have an authentication token specified.".format(username=dx_username,CONF_FILE=CONF_FILE))
	return True


def log_into_dnanexus(dx_username):
	""" 
	Function : Logs a user into DNAnexus.
	Args     : dx_username - str. The login name of a DNAnexus user.
	Returns  : None.
	Raises   : subprocess.CalledProcessError if logging in fails.
	"""
	dx_username = strip_dx_userprefix(dx_username)	
	validate_username(dx_username,exception=True)

	#"module load gbsc/dnanexus/current" to get the script log_into_dnanexus.sh
	subprocess.check_call("log_into_dnanexus.sh -u {du}".format(du=dx_username),shell=True)

class Utils:
	def __init__(self,dx_username):
		"""
		Args : dx_username - The login name of the DNAnexus user.
		"""
		log_into_dnanexus(dx_username)
		dx_username = add_dx_userprefix(dx_username)
		self.dx_username = dx_username

	def invite_user_to_org_projects(self,org,invitee,created_after,access_level,send_email=False):
		"""
		Function : Invites the specified DNAnexus user (the invitee) to all projects in the specified org with the specified access level. 
						   The dxpy invite method call is idempotent, nonetheless, only projects belonging to the org where the invitee 
							 doesn't have the specified access level are processed. Note that the user making this called should be an admin
							 of the org - thus the instantiation of this class should be with dx_username set to a DNAnexus admin user name.
		Args     : created_after : Date (e.g. 2012-01-01) or integer timestamp after which the project was created 
								  (negative number means in the past, or use suffix s, m, h, d, w, M, y)")
							 org - str. The name of the DNAnexus org to search for projects to invite the user to. 
							 invitee - str. The login name of the DNAnexus user to receive the invitations to the projects in the org. 
							 access_level  : str. One of ["VIEW","UPLOAD","CONTRIBUTE","ADMINISTER"], which specifies the ermission level the new 
									member should have on shared projects. See https://wiki.dnanexus.com/API-Specification-v1.0.0/Project-Permissions-and-Sharing for details on the different access levels.
							 send_email - bool. True means to let the dxpy API send an email notification to the user for each project they are
									invited to.
		Returns  : list of the projects that the user was invited to.
		"""
		org = add_dx_orgprefix(org)
		invitee = add_dx_userprefix(invitee)
		#get projects since created_after date
		gen = dxpy.org_find_projects(org_id=org,created_after=created_after)
		#gen is a generator of dicts of the form 
		# {u'level': u'NONE', u'id': u'project-ByQ8kj8028GJ182PZx95Z3G2', u'public': False}
		projects_invited_to = []
		for i in gen:
			current_level = i["level"]
			if current_level != access_level:
				project = dxpy.DXProject(i["id"])
				project.invite(invitee=invitee,level=access_level,send_email=send_email)
				projects_invited_to.append(project.name)
		return projects_invited_to
	
	
