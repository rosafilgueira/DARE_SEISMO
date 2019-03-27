#!/bin/bash
# decomposes mesh using the pre-saved mesh files in MESH-default
echo
echo "  decomposing mesh..."
echo
./bin/xdecompose_mesh $NPROC ./DATA/mesh_homogeneous $BASEMPIDIR

