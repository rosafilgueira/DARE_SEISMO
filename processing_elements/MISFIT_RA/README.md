# Create a python3 conda enviroment

```
conda create -n mypython3 python=3

```
# Activate the conda enviroment
```
conda activate mypython3
```

# Install obspy and dispel4py
```
conda install basemap
conda config --add channels conda-forge
conda update -n base -c defaults conda
conda install obspy
```

# Clone and Install dispel4py from the gitlab repo
```
git clone https://gitlab.com/project-dare/dispel4py
cd dispel4py
python setup.py install
cd ..
```

# Clone WP6_EPOS repo 
```
git clone https://gitlab.com/project-dare/WP6_EPOS.git
cd  WP6_EPOS/processing_elements/MISFIT_RA
```

# Run dispel4py workflows - you can use the following scripts to simplify the process
## Note --> you will need to change the paths inside misfit_input.jsn (and have already the misfit input data, which is not in this repo)
```
./run_preprocess_misfit.sh
./run_RA.sh
```

# Test the misfit preprocess workflow using a Notebook (misfit_notebook)
## create a python kernel to work with your conda enviroment -- later you will need to select this kernel to run the Jupyter Notebook
```
conda install ipykernel
python -m ipykernel install --user --name mypthon3 --display-name mpython3
```
