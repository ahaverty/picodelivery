#!/bin/bash

echo "Deleting the content of the area_data folder, containing the swarmed data, aggregate csv files and any saved models."
read -p "Are you sure you want to continue with the delete? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	`rm -rf ../area_data/*`
	echo "'area_data' folder deleted."
else
	echo "Cancelling delete, exiting..."
fi
