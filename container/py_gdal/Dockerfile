FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y

RUN apt-get install gdal-bin libgdal-dev libproj-dev proj-bin -y

RUN apt-get clean all

WORKDIR /usr/src/app

RUN conda update conda

RUN conda config --set channel_priority strict

ADD requirements.txt /usr/src/app/requirements.txt

RUN conda create -n spatialmos -c anaconda --file /usr/src/app/requirements.txt

RUN conda init bash

RUN echo "source activate spatialmos" > ~/.bashrc

ENV PATH /opt/conda/envs/env/bin:$PATH