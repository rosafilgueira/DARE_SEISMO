#!/bin/bash

ls -la $STAGED_DATA

echo "Creating files in $STAGED_DATA"
mkdir -p $STAGED_DATA/misfit_data/data/
cp -r $INPUT_DIR/download_data/* $STAGED_DATA/misfit_data/
