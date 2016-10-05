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

import gbsc_dnanexus


#The environment module gbsc/gbsc_dnanexus/current should also be loaded in order to log into DNAnexus

DX_LOGIN_CONF = gbsc_dnanexus.CONF_FILE

description = "Invites a DNAnexus user to be a member of all projects billed to a the specified org, with the specified access level."
parser = ArgumentParser(description=description)
parser.add_argument('-u',"--user-name",required=True,help="The DNAnexus login user name to invite to projects owned by the org specified by --org. An API token must have already been generated for this user and that token must have been added to the DNAnexus login configuration file located at {DX_LOGIN_CONF}.".format(DX_LOGIN_CONF=DX_LOGIN_CONF))
parser.add_argument('-l','--access-level',required=True,choices=["VIEW","UPLOAD","CONTRIBUTE","ADMINISTER"],help="Permissions level the new member should have on shared projects.")
parser.add_argument('-o',"--org",required=True,help="The name of the DNAnexus organization that the projects belong to.")
parser.add_argument("--created-after",required=True,help="Date (e.g. 2012-01-01) or integer timestamp after which the project was created (negative number means in the past, or use suffix s, m, h, d, w, M, y)")
parser.add_argument("--log-file",required=True,help="The name of the log file.")

args = parser.parse_args()
org = args.org
user = args.user_name
access_level = args.access_level
created_after = args.created_after
logfile = args.log_file

script_dir,script_name = os.path.dirname(__file__),os.path.basename(__file__)

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

utils = gbsc_dnanexus.utils.Utils(dx_user_name=user)
invited_projects = utils.invite_user_to_org_projects(org=org,created_after=created_after,access_level=access_level)
for i in invited_projects:
	logger.info("Invited {user} to {project} with level {access_level}.".format(user=user,project=i,access_level=access_level))
