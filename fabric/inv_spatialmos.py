#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

from invoke import task, Collection
import inv_logging
import inv_docker

@task
def get_available_data_suedtirol(c):
    """Download data from South Tyrol."""
    inv_logging.task(get_available_data_suedtirol.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/suedtirol.py", "--beginndate", "2018-01-01", "--enddate", "2019-01-10"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_suedtirol.__name__)

@task
def get_available_data_uibk(c):
    """Download data from uibk."""
    inv_logging.task(get_available_data_uibk.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/uibk.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_uibk.__name__)

spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(get_available_data_suedtirol)
spatialmos_development_ns.add_task(get_available_data_uibk)

spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(get_available_data_suedtirol)
spatialmos_production_ns.add_task(get_available_data_uibk)
