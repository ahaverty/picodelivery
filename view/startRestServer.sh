#!/bin/bash

logDirName="logs"
mkdir -p $logDirName
logFilename="restapi_`date +%s`.txt"

cd restservice
nodejs restapi.js >> ../$logDirName/$logFilename 2>&1 &
cd ..

echo "Printing output to $logDirName/$logFilename"
