#!/bin/bash

aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId'

aws ec2 start-instances --instance-ids $(aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId' | tr '\n' ' ')
