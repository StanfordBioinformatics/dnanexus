#!/bin/bash -e
#can't set the -u flag because the dnanexus environment.sh script sets unbound variables that will trigger an error.

###
#Nathaniel Watson
#July 5, 2016
#nathankw@stanford.edu
###

###ENVIRONMENT VARIABLES###
#The following environment variables must have been previously set:
# 1) DXT - Specifies the path to the environment.sh file to source in the dx-toolkit software.
#					 This is set by loading the environment module dx-toolkit/dx-toolit.
# 2) DX_LOGIN_CONF - Specifies the path to the dnanexus_conf.json file in the gbsc_dnanexus software. 
#					 This is set by loading the environment module gbsc/gbsc_dnanexus/current.
###

DX_LOGIN_CONF=$(pwd)/../dnanexus_conf.json

source $DXT 
module load jq/1.5

set -eu -o pipefail


function help() {
	echo "Program:"
	echo "  Logs the user into DNAnexus."
	echo -e "\nArgs:"
	echo -e "  -u: Required. Your DNAnexus username, which must appear in ${DX_LOGIN_CONF} in order to identify the DNAnexus API token."
	echo -e "      If your username doesn't appear there, add it along with your API key."
}

username=
while getopts "u:h" opt
do
	case $opt in 
		h) help;
			 exit 0
			 ;;
		u) username=$OPTARG
			;;
	esac
done

if [[ -z $username ]]
then
	echo "You must supply a username to the -u argument."
	exit 1
fi

auth_token=$(jq -r ".${username}" ${DX_LOGIN_CONF})

dx login --token $auth_token --noprojects

echo "Successfully logged into DNAnexus as $(dx whoami)"

