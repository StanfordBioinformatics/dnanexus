#!/usr/bin/env python

###
#Nathaniel Watson
#Stanford School of Medicine
#August 17, 2016
#nathankw@stanford.edu
###

import os
import sys
from argparse import ArgumentParser
import subprocess
import logging

import dxpy


#The environment module gbsc/dnanexus/current should also be loaded in order to log into DNAnexus

DX_LOGIN_CONF = os.getenv("DX_LOGIN_CONF") #exported by the env module gbsc/dnanexus_seqresults

description = ""
parser = ArgumentParser(description=description)
parser.add_argument('-u',"--user-name",required=True,help="DNAnexus user name. The login name of the DNAnexus account. An API token must have already been generated for this user and that token must have been added to the DNAnexus login configuration file located at {DX_LOGIN_CONF}.".format(DX_LOGIN_CONF=DX_LOGIN_CONF))
parser.add_argument('-l','--access-level',required=True,choices=["VIEW","UPLOAD","CONTRIBUTE","ADMINISTER"],help="Permissions level the new member should have")
parser.add_argument('-o',"--org",required=True,help="The name of the DNAnexus organization that the projects belong to.")
parser.add_argument("--created-after",required=True,help="Date (e.g. 2012-01-01) or integer timestamp after which the project was created (negative number means in the past, or use suffix s, m, h, d, w, M, y)")

args = parser.parse_args()
org = args.org
user = args.user_name
level = args.access_level
created_after = args.created_after

#LOG into DNAnexus (The environment module gbsc/dnanexus_seqresults should also be loaded in order to log into DNAnexus)
subprocess.check_call("log_into_dnanexus.sh -u {du}".format(du=user),shell=True)
internal_dx_username = "user-" + user

script_dir,script_name = os.path.dirname(__file__),os.path.basename(__file__)
logfile = os.path.join(script_dir,"log_" + user + "_" + os.path.splitext(script_name)[1] + ".txt")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:   %(message)s')
fhandler = logging.FileHandler(filename=logfile,mode='a')
fhandler.setLevel(logging.INFO)
fhandler.setFormatter(formatter)
chandler = logging.StreamHandler(sys.stdout)
chandler.setLevel(logging.DEBUG)
chandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.addHandler(chandler)

#get projects since created_after date
gen = dxpy.org_find_projects(org_id=org,created_after=created_after)
#gen is a generator of dicts of the form 
# {u'level': u'NONE', u'id': u'project-ByQ8kj8028GJ182PZx95Z3G2', u'public': False}

#invite user to projects
for i in gen:
	current_level = i["level"]
	if current_level != level:
		project = dxpy.DXProject(i["id"])
		project.invite(invitee=internal_dx_username,level=level,send_email=False)
		logger.info("Invited {user} to {project_name} with level {level}.".format(user=internal_dx_username,project_name=project.name,level=level))	
