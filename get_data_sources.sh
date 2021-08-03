#!/bin/sh
# get data source files

DATA_SOURCES_PATH='data_sources/'
DATA_SOURCES='../data_links'

mkdir $DATA_SOURCES_PATH
cd $DATA_SOURCES_PATH

xargs -n 1 curl -s -O < $DATA_SOURCES

cd ..
