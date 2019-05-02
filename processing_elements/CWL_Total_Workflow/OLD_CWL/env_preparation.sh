#!/bin/bash

echo "running example: `date`"
currentdir=`pwd`

# sets up directory structure in current example directory
echo
echo "   setting up example..."
echo

#!/bin/bash

mkdir -p $ENV_DATA/misfit_data
rm -r $ENV_DATA/misfit_data/data
rm -r $ENV_DATA/misfit_data/stations
rm -r $ENV_DATA/misfit_data/output
rm -r $ENV_DATA/misfit_data/output-images
mkdir $ENV_DATA/misfit_data/output

rm -rf $ENV_DATA/GM
mkdir -p $ENV_DATA/GM
