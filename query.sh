#!/bin/bash
#!/usr/bin/python3


# This file should accept querys and return the original input lines that match the query, with results seperated by newlines.
# Multiple filters may be provided and should be handled via logical AND. E.G user 5 and node 2 should return all results lines
# submitted on node 2 for user 5.
#
#

# Below is preprepared code to accept the command line arguments we will be providding to this file. The rest is up to you.

# Change directory to where the script is stored, not where it is run from
scriptPath=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $scriptPath
source participantConfig.sh
# This brought in the following variables
# $chainName
# $rpcuser
# $rpcpassword
# $rpcport

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

show_help() {
cat << EOF
Usage: ${0##*/} [--filter arg]...
This command should have at least on option set. Mutliple options may also be set.

    -h                                          display this help and exit
    --start_time <arg> | --start_time=<arg> 	Filter this query to entries >= start_time
    --end_time <arg> | --end_time=<arg>     	Filter this query to entries <= end_time
    --node <arg> | --node=<arg>             	Filter this query by node
    --id <arg> | --id=<arg>                 	Filter this query by id
    --ref_id <arg> | --ref_id=<arg>         	Filter this query by ref_id
    --user <arg> | --user=<arg>             	Filter this query by user
    --activity <arg> | --activity=<arg>     	Filter this query by activity
    --resource <arg> | --resource=<arg>         Filter this query by resource
    --sort_by <arg> | --sort_by=<arg>           Sort this query by provided column
    --order <arg> | --order=<arg>     	        Sort this query in 'asc' or 'desc' order
EOF
}

# Initialize all the option variables.
# This ensures we are not contaminated by variables from the environment.
start_time=
end_time=
node=
id=
ref_id=
user=
activity=
resource=
sort_by=
order=

# Process arguments and set variables.
while :; do
    case $1 in
        -h|-\?|--help)
            show_help    # Display a usage synopsis.
            exit
            ;;

        --start_time)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                start_time=$2
                shift
            else
                die 'ERROR: "--start_time" requires a non-empty option argument.'
            fi
            ;;
        --start_time=?*)
            start_time=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --start_time=)         # Handle the case of an empty --arg=
            die 'ERROR: "--start_time" requires a non-empty option argument.'
            ;;


        --end_time)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                end_time=$2
                shift
            else
                die 'ERROR: "--end_time" requires a non-empty option argument.'
            fi
            ;;
        --end_time=?*)
            end_time=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --end_time=)         # Handle the case of an empty --arg=
            die 'ERROR: "--end_time" requires a non-empty option argument.'
            ;;

        --node)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                node=$2
                shift
            else
                die 'ERROR: "--node" requires a non-empty option argument.'
            fi
            ;;
        --node=?*)
            node=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --node=)         # Handle the case of an empty --arg=
            die 'ERROR: "--node" requires a non-empty option argument.'
            ;;

        -i|--id)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                id=$2
                shift
            else
                die 'ERROR: "--id" requires a non-empty option argument.'
            fi
            ;;
        --id=?*)
            id=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --id=)         # Handle the case of an empty --arg=
            die 'ERROR: "--id" requires a non-empty option argument.'
            ;;

        --ref_id)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                ref_id=$2
                shift
            else
                die 'ERROR: "--ref_id" requires a non-empty option argument.'
            fi
            ;;
        --ref_id=?*)
            ref_id=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --ref_id=)         # Handle the case of an empty --arg=
            die 'ERROR: "--ref_id" requires a non-empty option argument.'
            ;;

        --user)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                user=$2
                shift
            else
                die 'ERROR: "--user" requires a non-empty option argument.'
            fi
            ;;
        --user=?*)
            user=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --user=)         # Handle the case of an empty --arg=
            die 'ERROR: "--user" requires a non-empty option argument.'
            ;;

        --activity)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                activity=$2
                shift
            else
                die 'ERROR: "--activity" requires a non-empty option argument.'
            fi
            ;;
        --activity=?*)
            activity=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --activity=)         # Handle the case of an empty --arg=
            die 'ERROR: "--activity" requires a non-empty option argument.'
            ;;

        --resource)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                resource=$2
                shift
            else
                die 'ERROR: "--resource" requires a non-empty option argument.'
            fi
            ;;
        --resource=?*)
            resource=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --resource=)         # Handle the case of an empty --arg=
            die 'ERROR: "--resource" requires a non-empty option argument.'
            ;;

        --sort_by)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                sort_by=$2
                shift
            else
                die 'ERROR: "--sort_by" requires a non-empty option argument.'
            fi
            ;;
        --sort_by=?*)
            sort_by=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --sort_by=)         # Handle the case of an empty --arg=
            die 'ERROR: "--sort_by" requires a non-empty option argument.'
            ;;

        --order)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                order=$2
                shift
            else
                die 'ERROR: "--order" requires a non-empty option argument.'
            fi
            ;;
        --order=?*)
            order=${1#*=} # Delete everything up to "=" and assign the remainder.
            ;;
        --order=)         # Handle the case of an empty --arg=
            die 'ERROR: "--order" requires a non-empty option argument.'
            ;;

        --)              # End of all options.
            shift
            break
            ;;
        -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
            ;;
        *)               # Default case: No more options, so break out of the loop.
            break
    esac

    shift
done

# =====================================================
# Place your code below this comment block
#
# The following variables have been set for you.
# $chainName        The name of the chain
# $rpcuser          The rpc username for the chain
# $rpcpassword      The rpc password for the chain
# $rpcport          The rpc port for the chain
# $start_time       Filter this query to entries >= start_time
# $end_time         Filter this query to entries <= end_time
# $node             Filter this query by node
# $id               Filter this query by id
# $ref_id           Filter this query by ref_id
# $user             Filter this query by user
# $activity         Filter this query by activity
# $resource         Filter this query by resource
# $sort_by          Sort this query by provided column
# $order            Sort this query in 'asc' or 'desc' order
#
#
# example code
# java -jar myQuery.jar $chainName $rpcuser $rpcport $rpcpassword \
# st=$start_time \
# et=$end_time \
# node=$node \
# id=$id \
# ref=$ref_id \
# user=$user \
# act=$activity \
# res=$resource \
# sort=$sort_by \
# order=$order
# =====================================================
#export PYTHONPATH=$HOME/python_packages

python3 $scriptPath/MyCode/queryChain.py $chainName $rpcuser $rpcpassword $rpcport \
startTime=$start_time \
endTime=$end_time \
node=$node \
id=$id \
ref_id=$ref_id \
user=$user \
activity=$activity \
resource=$resource \
sortKey=$sort_by \
sortOrder=$order
