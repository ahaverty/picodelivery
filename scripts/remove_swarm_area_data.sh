#!/bin/bash

# Script for quickly removing the area data (i.e. nupics models and swarm data)
# Should only be ran if you redoing the models and swarms
# (Costly mistake otherwise!)
# @author alanhaverty@student.dit.ie

echo "Deleting the content of the area_data folder, containing the swarmed data, aggregate csv files and any saved models."
echo "These folders contain a lot of prediction data that is not easily replaced."
read -p "ARE YOU SURE you want to continue with the delete? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	`rm -rf ../area_data/*`
	echo "'area_data' folder deleted."
else
	echo "Cancelling delete, exiting..."
fi
