#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

import os
import sys
import requests
import logging
from invoke import task, Collection
import inv_logging
import inv_docker


@task
def spatialmos__init_topography(c):
    """Create shapefiles for spatialMOS"""
    inv_logging.task(spatialmos__init_topography.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/init_shapefiles.R"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)

    cmd = ["py_pre_processing_topography", "/opt/conda/envs/spatialmos/bin/python", "./py_spatialmos/pre_processing_topography.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)

    # Download Shapefile and unzip it
    if not os.path.exists("./data/get_available_data/gadm/gadm36_AUT_shp"):
        req_gadm36_zip_file = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AUT_shp.zip"
        gadm36_zip_file = "./data/get_available_data/gadm/gadm36_AUT_shp.zip"
        req_shapefile = requests.get(req_gadm36_zip_file, stream=True)
        if req_shapefile.status_code == 200:
            with open(gadm36_zip_file, mode="wb") as f:
                for chunk in req_shapefile.iter_content(chunk_size=128):
                    f.write(chunk)
            logging.info("The shapefile '%s' has been downloaded.", req_gadm36_zip_file)
            c.run(f"unzip {gadm36_zip_file} -d ./data/get_available_data/gadm/gadm36_AUT_shp")
        else:
            logging.error("There was a problem with the download of the shapefile '%s'", req_gadm36_zip_file)
            sys.exit(1)

    inv_logging.success(spatialmos__init_topography.__name__)


@task
def py_spatialmos__archive_available_data(c, folder):
    """The csv-files are created with the 7zip. The folder must be specified e.g. uibk."""
    inv_logging.task(py_spatialmos__archive_available_data.__name__)
    command = ["python", "./py_spatialmos/archive_available_data.py", "--folder", folder]
    command = ' '.join(command)
    c.run(command)
    inv_logging.success(py_spatialmos__archive_available_data.__name__)


@task
def py_spatialmos__get_gefs(c, date, runhour, parameter, avgspr):
    """Download data gefs files."""
    inv_logging.task(py_spatialmos__get_gefs.__name__)
    cmd = ["py_wgrbi2", "python", "./py_spatialmos/get_gefs_forecasts.py", "--date", date, "--runhour", runhour, "--parameter", parameter, "--avgspr", avgspr]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_gefs.__name__)

@task
def py_spatialmos__get_suedtirol(c, begindate, enddate):
    """Download data from South Tyrol."""
    inv_logging.task(py_spatialmos__get_suedtirol.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_suedtirol_data.py",
           "--begindate", begindate, "--enddate", enddate]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_suedtirol.__name__)


@task
def py_spatialmos__get_uibk(c):
    """Download data from uibk."""
    inv_logging.task(py_spatialmos__get_uibk.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_uibk_data.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_uibk.__name__)


@task
def py_spatialmos__get_wetter_at(c, begindate, enddate):
    """Download data from wetter_at."""
    inv_logging.task(py_spatialmos__get_wetter_at.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_wetter_at_data.py",
           "--begindate", begindate, "--enddate", enddate]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_wetter_at.__name__)


@task
def py_spatialmos__get_zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(py_spatialmos__get_zamg.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_zamg_data.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_zamg.__name__)

@task
def py_spatialmos__pre_processing_reforecasts(c, parameter):
    """GEFS Reforecasts are bilinear interpolated at station locations."""
    inv_logging.task(py_spatialmos__pre_processing_reforecasts.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_gefs_reforecasts_to_station_locations.py", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_processing_reforecasts.__name__)


@task
def py_spatialmos__pre_processing_observations_and_reforecasts_to_stations(c):
    """Station Observations and GEFS Reforecasts are combined."""
    inv_logging.task(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_station_observations_and_reforecasts.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations.__name__)

@task
def py_spatialmos__pre_processing_gamlss_crch_climatologies(c, parameter):
    """Create climatologies for further processing in R with gamlss."""
    inv_logging.task(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_gamlss_crch_climatologies.py", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__)


@task
def r_spatialmos__gamlss_crch_model(c, parameter, validation):
    """Create the required spatial climatologies."""
    inv_logging.task(r_spatialmos__gamlss_crch_model.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/gamlss_crch_model.R", "--parameter", parameter, "--validation", validation]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__gamlss_crch_model.__name__)

@task
def r_spatialmos__spatial_climatologies_nwp(c, parameter, begin, end):
    """Create daily climatologies for the NWP."""
    inv_logging.task(r_spatialmos__spatial_climatologies_nwp.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/spatial_climatologies_nwp.R", "--parameter", parameter, "--begin", begin, "--end", end]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_nwp.__name__)

@task
def r_spatialmos__spatial_climatologies_obs(c, parameter, begin, end):
    """Create daily climatologies for the observations."""
    inv_logging.task(r_spatialmos__spatial_climatologies_obs.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/spatial_climatologies_observations.R", "--parameter", parameter, "--begin", begin, "--end", end]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_obs.__name__)

@task
def py_spatialmos__pre_proccessing_gribfiles(c, date, parameter):
    """Create the csv file and the jsonfile from the avalible gribfiles."""
    inv_logging.task(py_spatialmos__pre_proccessing_gribfiles.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_prediciton.py", "--date", date, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_proccessing_gribfiles.__name__)

@task
def py_spatialmos__prediction(c, date, parameter):
    """Create the predictions and the spatialMOS plots."""
    inv_logging.task(py_spatialmos__prediction.__name__)
    cmd = ["py_prediction", "/opt/conda/envs/spatialmos/bin/python", "./py_spatialmos/prediction.py", "--date", date, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__prediction.__name__)


spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(spatialmos__init_topography)
spatialmos_development_ns.add_task(py_spatialmos__archive_available_data)
spatialmos_development_ns.add_task(py_spatialmos__get_gefs)
spatialmos_development_ns.add_task(py_spatialmos__get_suedtirol)
spatialmos_development_ns.add_task(py_spatialmos__get_uibk)
spatialmos_development_ns.add_task(py_spatialmos__get_wetter_at)
spatialmos_development_ns.add_task(py_spatialmos__get_zamg)
spatialmos_development_ns.add_task(py_spatialmos__pre_processing_reforecasts)
spatialmos_development_ns.add_task(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations)
spatialmos_development_ns.add_task(py_spatialmos__pre_processing_gamlss_crch_climatologies)
spatialmos_development_ns.add_task(py_spatialmos__pre_proccessing_gribfiles)
spatialmos_development_ns.add_task(py_spatialmos__prediction)
spatialmos_development_ns.add_task(r_spatialmos__gamlss_crch_model)
spatialmos_development_ns.add_task(r_spatialmos__spatial_climatologies_nwp)
spatialmos_development_ns.add_task(r_spatialmos__spatial_climatologies_obs)


spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(py_spatialmos__archive_available_data)
spatialmos_production_ns.add_task(py_spatialmos__get_gefs)
spatialmos_production_ns.add_task(py_spatialmos__get_uibk)
spatialmos_production_ns.add_task(py_spatialmos__get_zamg)
spatialmos_production_ns.add_task(py_spatialmos__prediction)
