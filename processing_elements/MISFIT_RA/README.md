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

# Run dispel4py workflows

The following scripts to simplify the process of running *create_misfit_prep.py* and  *dispel4py_RA.pgm_story.py* workflows 
Paths inside misfit_input.jsn need to be changed. And also it is needed to have a copy  of the misfit input data, which is not in this repo.

```
./run_preprocess_misfit.sh
./run_RA.sh
```

# Test the misfit preprocess workflow using a Notebook (misfit_notebook)

Create a python kernel to work with the conda enviroment and select it later in the Jupyter Notebook browser to run the notebook.

```
conda install ipykernel
python -m ipykernel install --user --name mypthon3 --display-name mpython3
```
