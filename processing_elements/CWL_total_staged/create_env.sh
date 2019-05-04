#!/bin/bash

mkdir -p $STAGED_DATA/misfit_data
rm -rf $STAGED_DATA/misfit_data/data
rm -rf $STAGED_DATA/misfit_data/stations
rm -rf $STAGED_DATA/misfit_data/output
rm -rf $STAGED_DATA/misfit_data/output-images
mkdir $STAGED_DATA/misfit_data/output

rm -rf $STAGED_DATA/GM
mkdir -p $STAGED_DATA/GM

cp $INPUT_DIR/processing.json $STAGED_DATA/misfit_data
