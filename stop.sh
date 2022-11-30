#!/bin/bash

INSTANCES=$(aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId')

echo aws ec2 stop-instances --instance-ids $(aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId' | tr '\n' ' ')
