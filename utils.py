import subprocess
import os

import dxpy

DX_USER_PREFIX = "user-"
DX_ORG_PREFIX = "org-"

class DxProjectNotFound(Exception):                                                
  pass                                                                             
                                                                                   
class DxApiKeyNotFound(Exception):                                                 
  """                                                                              
  Raised when the environment variable DX_SECURITY_CONTEXT isn't set.              
  """                                                                              
  #Set message to be static (this will always be the error message when this Exception is raised:
  message = "Environment variable DX_SECURITY_CONTEXT not set. This is needed to store your API key for authenticating at the DNAnexus authentication server; see http://autodoc.dnanexus.com/bindings/python/current/dxpy.html?highlight=token for details."

class UnknownDNAnexusUsername(Exception):
  pass

class InvalidAuthToken(Exception):
  pass

def get_dx_username(strip_prefix=False):
  """
  Uses the API token specified in the DX_SECURITY_CONTEXT environment variable (http://autodoc.dnanexus.com/bindings/python/current/dxpy.html?highlight=token).
  You can set this variable as follows un Unix platforms: 
    export DX_SECURITY_CONTEXT="{\"auth_token_type\": \"Bearer\", \"auth_token\": \"your_token\"}"

  Args: strip_prefix: bool. True means to strip out the DNAnexus prefix added to all user names, being 'user-'. 
  """
  env_var = "DX_SECURITY_CONTEXT"
  if not env_var in os.environ:
    raise DxApiKeyNotFound
  user = dxpy.whoami()
  if strip_prefix:
    return user.split("-")[-1]
  return user

def add_props_to_file(project_id,file_id,props):
  """
  Args: project_id - The DNAnexus project ID in which file_id belongs.
        file_id    - The ID of the file in DNAnexus to which the props are to be added.
        props      - dict. The props to add to the file.
  """
  dxpy.api.file_set_properties(object_id=file_id,input_params={"project": project_id,"properties": props})  

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
  Returns  : dict. where the keys are the names of the projects that the user was invited to, and the values are the IDs of
             the projects.
  """
  org = add_dx_orgprefix(org)
  invitee = add_dx_userprefix(invitee)
  #get projects since created_after date
  gen = dxpy.org_find_projects(org_id=org,created_after=created_after)
  #gen is a generator of dicts of the form 
  # {u'level': u'NONE', u'id': u'project-ByQ8kj8028GJ182PZx95Z3G2', u'public': False}
  projects_invited_to = {}
  for i in gen:
    current_level = i["level"]
    if current_level != access_level:
      project = dxpy.DXProject(i["id"])
      project.invite(invitee=invitee,level=access_level,send_email=send_email)
      projects_invited_to[project.name] = project.id
  return projects_invited_to
  
  
def select_newest_project(dx_project_ids):
  """ 
  Function : Given a list of DNAnexus project IDs, returns the one that is newest as determined by creation date.
  Args     : dx_project_ids: list of DNAnexus project IDs.
  Returns  : dxpy.DXProject instance.
  """
  if len(dx_project_ids) == 1:
    return dx_project_ids[0]
  
  projects = [dxpy.DXProject(x) for x in dx_project_ids]
  created_times = [x.describe()["created"] for x in projects]
  paired = zip(created_times,projects)
  paired.sort(reverse=True)
  return paired[0][1]
