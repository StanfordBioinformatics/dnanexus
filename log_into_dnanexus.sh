#!/bin/bash 

###
#Nathaniel Watson
#July 5, 2016
#nathankw@stanford.edu
###

source $DXT #set by env. module dx-toolkit/dx-toolit, which is loaded by env. module gbsc/dnanexus/current
module load jq/1.5

set -eu -o pipefail

dx_user_conf=$(dirname $0)/dnanexus_conf.json 

function help() {
	echo "Program:"
	echo "  Logs the user into DNAnexus."
	echo -e "\nArgs:"
	echo -e "  -u: Required. Your DNAnexus username, which must appear in $dx_user_conf in order to identify the DNAnexus API token."
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

auth_token=$(jq -r ".${username}" $dx_user_conf)

dx login --token $auth_token --noprojects

dx whoami

