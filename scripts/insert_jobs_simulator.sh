#!/bin/bash

scriptDir="/home/picodelivery/picodelivery/scripts"
logDir=$scriptDir"/logs"
crontabLogDir=$logDir"/crontab"

mkdir -p $crontabLogDir
cd $scriptDir
mkdir -p lock

#echo "Starting insert_jobs_simulator.py" >> $crontabLogDir/crontab_insert_jobs_simulator_$(date +\%Y\%m\%d\%H\%M).txt 2>&1
#python $scriptDir/insert_jobs_simulator.py >> $crontabLogDir/crontab_insert_jobs_simulator_$(date +\%Y\%m\%d\%H\%M).txt 2>&1


(
	flock -x -w 10 200 || exit 1
	
	python $scriptDir/insert_jobs_simulator.py
	#2>> $crontabLogDir/crontab_insert_jobs_simulator_$(date +\%Y\%m\%d\%H\%M).txt

) 200>lock/insert_jobs_simulator.filelock
