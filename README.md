# PicoDelivery System, Database, NuPIC, and simulator script repository

As part of Alan Haverty's DT2114C Final Year Project for Dublin Institute of Technology.

## About this repo
<b>Contents:</b>  
<b>1. area_data folder:  </b>
   Folder required by the swarm and run scripts to persist prediction related data  
<b>2. backand folder:  </b>
Configuration export from Backand.com along with human readable extracts
of the scripts developed within Backand.com's editors  
<b>3. configuration folder:  </b>
    Contains the sql modules used in the python scripts,
and the placeholder swarm_description file, used in the swarming process.  
<b>4. database folder:  </b>
    Contains the dump of the table, triggers, and procedures used to create the MySQL database for the project  
<b>5. picodelivery folder:</b>  
    Contains the python classes used in the python scripts
(database, config, logger helpers, and the nupic run.py class)  
<b>6. scripts folder:</b>  
    The various scripts used on the Ubuntu environment
(Data generators, simulators, NuPIC swarming and predictions, trigger and controller scripts)  
<b>7. Everything else:  </b>  
Project configuration ini, containing the variables and job rate graph array  
Requirements txt, contains the requirements needed to run the scripts on an Ubuntu Server with MySQL
Setup.py, used to install this repo using: _python setup.py install_