#!/bin/bash

echo "running example: `date`"
currentdir=`pwd`

# sets up directory structure in current example directory
echo
echo "   setting up example..."
echo

#!/bin/bash

mkdir -p $STAGED_DATA/misfit_data
rm -r $STAGED_DATA/misfit_data/data
rm -r $STAGED_DATA/misfit_data/stations
rm -r $STAGED_DATA/misfit_data/output
rm -r $STAGED_DATA/misfit_data/output-images
mkdir $STAGED_DATA/misfit_data/output

rm -rf $STAGED_DATA/GM
mkdir -p $STAGED_DATA/GM
