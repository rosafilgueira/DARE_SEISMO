!/bin/bash
set -x
echo "running example: `date`"
currentdir=`pwd`

# sets up directory structure in current example directory
echo
echo "   setting up example..."
echo

# cleans output files
mkdir -p $STAGED_DATA/results/OUTPUT_FILES
rm -rf $STAGED_DATA/results/OUTPUT_FILES/*

# links executables

# stores setup
cp -r $INPUT_DIR/specfem3d_test_input/DATA $STAGED_DATA/results/.

mkdir -p $STAGED_DATA/results/bin
ln -s  $SPECFEM3D_HOME/bin/* $STAGED_DATA/results/bin/.

echo "!!!!!!!" $currentdir

# get the number of processors, ignoring comments in the Par_file
NPROC=`grep ^NPROC $INPUT_DIR/specfem3d_test_input/DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`

BASEMP=`grep ^LOCAL_PATH $INPUT_DIR/specfem3d_test_input/DATA/Par_file | cut -d = -f 2 `
BASEMPIDIR="$(echo -e "${BASEMP}" | sed -e 's/^[[:space:]]*//')"
echo $BASEMPDIR
mkdir -p $STAGED_DATA/results/$BASEMPIDIR

# decomposes mesh using the pre-saved mesh files in MESH-default
echo
echo "  decomposing mesh..."
echo


cd $STAGED_DATA/results
./bin/xdecompose_mesh $NPROC ./DATA/mesh_homogeneous $BASEMPIDIR

