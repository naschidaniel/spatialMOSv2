#!/bin/bash
#$ -cwd
#$ -M daniel@naschi.at

INSTALLFOLDER=$(grep INSTALLFOLDER .env | cut -d '=' -f 2-)
HOST=$(grep HOST .env | cut -d '=' -f 2-)


# - Starting the job here
cd $INSTALLFOLDER
./task.py production.spatialmos.py_archive_get_available_data "gefs"
