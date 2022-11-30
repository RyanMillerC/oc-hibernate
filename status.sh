#!/bin/bash
#
# This is bad. This is a hack. Don't do this. Don't be like Ryan.

INSTANCES=$(aws ec2 describe-instances | jq -r '.Reservations[].Instances')

INSTANCE_NAMES=$(echo "$INSTANCES" | jq -r '.[].Tags[].Value' | sed '/^cluster-*/!d')
INSTANCE_STATUSES=$(echo "$INSTANCES" | jq -r '.[].State.Name')

# echo $INSTANCES | jq -r '.[].Tags[].Value as $value | if ($value == "cluster-.*") then $value else $value end' # , .[].State.Name' # | sed '/^cluster-*/!d'

echo $INSTANCES | jq -r '.[] | .State.Name, (.Tags[] | select(.Value | test("^cluster-.*")) | .Value)'

# OLD_IFS="$IFS"
# IFS="\n"
# for INDEX in "${!INSTANCE_NAMES[@]}" ; do
#     echo $INDEX
#     echo "${INSTANCE_NAMES[INDEX]} ${INSTANCE_STATUSES[INDEX]}"
# done
# IFS="$OLD_IFS"
