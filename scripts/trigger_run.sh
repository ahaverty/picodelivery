#!/bin/bash

# Script to start the trigger_run.py python script
# author alanhaverty@student.dit.ie

scriptDir="/home/picodelivery/picodelivery/scripts"
logDir=$scriptDir"/logs"
crontabLogDir=$logDir"/crontab"

mkdir -p $crontabLogDir
cd $scriptDir
python $scriptDir/trigger_run.py >> $crontabLogDir/crontab_trigger_run_$(date +\%Y\%m\%d\%H\%M).txt 2>&1
