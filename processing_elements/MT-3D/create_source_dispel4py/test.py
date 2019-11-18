#!/usr/bin/env python
# coding: utf-8

# ### Using the create_source function
# This notebook should give an overview of the features of create_source.
# 

# Import python class $\textit{create_source}$ from libary

# In[10]:


from util import create_source


# Define path to CMTSOLUTION file. There are three options:
# 
# 1. **read** from local file
# 2. **download** from .zip file
# 3. **create** from JSON file        
# 
# Select $\textit{file_url}$ path to CMTSOLUTION file and $\textit{out_url}$ to save the created files

# In[11]:


download_url = 'Data.zip'    
local_url = 'CMTSOLUTION'
json_url = 'Input.json'

out_url = 'Out'


# Define pertubation list like $[\Delta M_{ij},\Delta Z,\Delta \vec{x}]$
#                                           
# If set to None, the code uses a default pertubation defined by:                      
# $\Delta M_{ij}$ = max($M_{ij}$)                                         
# $\Delta Z$ = $\frac{Z}{5}$                                           
# $\Delta \vec{x}$ = $0.18^\circ$ for UTM or 20 km for carthesian (based on UTM flag settings)     
# If you add pertubations, it is possible to set $\Delta M_{ij}$ to 'auto'. The code will then use max($M_{ij}$) as 
# pertubation. Else add a value in dyne*cm (10^xx).
# We also included the flag UTM=True/False which accounts for unit differences witnin the coordinate system:
# * UTM = True: lat/lon is in UTM coordinates --> m
# * UTM = False: lat/lon is in Geo coordinates --> $^\circ$                             
# --> $1^\circ \approx 111 $ km 
# 
# Note: In respect of synthetic data reusability, a constant value for $\Delta M_{ij}$ indipendent of the API run ID would be preferable. This parameter only scales the signal Amplitude and can be easily changed later if the initial  pertubation is known. This can be implemented in a later step during the preprocessing step before the run of pycmt3d etc.                             
# This default setting is not usfull for the location, because it might be influenced by the resolution of the velocity model                                                      
# --> high resolution results in a small pertubation and reversed 

# In[12]:


pertubation = ['auto',3.0,20000]


# Choose number of derivatives:                                                    
# 6 $\Rightarrow$ Moment Tensor Elements                                                              
# 7 $\Rightarrow$ Moment Tensor Elements and depth                                            
# 9 $\Rightarrow$ Moment Tensor Elements and hypocenter location (depth, latitude, longitude)                         

# In[13]:


Npar = 9


# The class $\textit{create_source}$ currently offers one function, that can be customized in 3 different ways, depending on a label in the first position:                      
# $\textit{create_CMTSOLUTION("download", index)}$                                                     
# $\textit{create_CMTSOLUTION("load", index)}$                                                     
# $\textit{create_CMTSOLUTION("json",index)}$                                                   
# Parameter index governs the pertubated entry in the CMTSOLUTION file. If set to None, the original file is created.
# 

# Run with download access

# In[14]:


create_CMT = create_source(file_url=download_url,out_url=out_url+'_Download/',pertubation=pertubation,UTM=False)
for MTi in range(Npar):
    create_CMT.create_CMTSOLUTION("download", MTi)


