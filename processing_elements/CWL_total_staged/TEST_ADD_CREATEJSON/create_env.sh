#!/bin/bash

echo $STAGED_DATA
echo $INPUT_DIR

mkdir -p $STAGED_DATA/misfit_data
rm -rf $STAGED_DATA/misfit_data/data
rm -rf $STAGED_DATA/misfit_data/stations
rm -rf $STAGED_DATA/misfit_data/output
rm -rf $STAGED_DATA/misfit_data/output-images

mkdir $STAGED_DATA/misfit_data/output
mkdir -p $STAGED_DATA/misfit_data/data/
mkdir -p $STAGED_DATA/misfit_data/SPECFEMDATA/

rm -rf $STAGED_DATA/GM
mkdir -p $STAGED_DATA/GM

cp $INPUT_DIR/processing.json $STAGED_DATA/misfit_data
cp -r $INPUT_DIR/SPECFEMDATA $STAGED_DATA/misfit_data/.

cp $INPUT_DIR/misfit_data/events_simulation_CI_CI_test_0_1507128030823 $STAGED_DATA/misfit_data/.
cp -r $INPUT_DIR/misfit_data/synth $STAGED_DATA/misfit_data/.
