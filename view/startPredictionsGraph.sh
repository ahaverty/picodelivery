#!/bin/bash

logDirName="logs"
mkdir -p $logDirName
logFilename="predictionsGraph_`date +%s`.txt"


cd predictions
nodejs server.js >> ../$logDirName/$logFilename 2>&1 &
cd ..

sleep 3
echo "Starting..."

echo "Printing output to $logDirName/$logFilename"

echo "Tail of output:"
tail $logDirName/$logFilename

