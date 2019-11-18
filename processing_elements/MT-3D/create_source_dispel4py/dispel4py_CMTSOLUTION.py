#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright:
    Mike Lindner (mike.lindner@kit.edu), 2019
"""

from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ProducerPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.provenance import *  #prov

from obspy import UTCDateTime
import numpy as np
import os
import json
# used for calculation default pertubation based on maximum singe force
import math
# used in get_file_content
import zipfile
import requests


def create_dictionary(content):
    '''
        helper function to bring list_output to uniform format as defined in json
    '''
    list_output = {'event MT':{},'event location':{}}
    for line in content:
        info = line.split(':')
        if len(info) == 1: # header line, no : included
            PDE = info[0].split()
            list_output['event time'] = UTCDateTime(int(PDE[1]),int(PDE[2]),int(PDE[3]),int(PDE[4]),int(PDE[5]),
                                                    float(PDE[6]))
            list_output['event magnitude'] = {'mb':float(PDE[10]),
                                              'Ms':float(PDE[11])}
            list_output['event name'] = PDE[12]
        elif info[0][0] == 'M': # if entry are MT elements
            list_output['event MT'][info[0]] = float(info[1])
        elif len(info[0].split()) == 1: # lat,lon,depth has no space in its key and does not start with M
            list_output['event location'][info[0]] = float(info[1])
        elif info[0] != 'event name': # write time shift and half duration information to dictionary
            list_output[info[0]] = float(info[1])
    return list_output

def download_file_content(file_url=None,fname=None):
    '''
        download .zip file and extract CMTSOLUTION information
        This Function is based on Emanuelles create_download_json.py code
    '''
    try:
        try:
            response = requests.get(file_url)
            zfiles=zipfile.ZipFile(io.BytesIO(response.content))
        except:
            zfiles=zipfile.ZipFile(file_url)
        listfile = zfiles.namelist()
    except:
        print('ERROR: Error reading zip file %s' % file_url)
    
    list_output = {}
    try:
        parfound=False
        for f in listfile:
            if fname in f:
                content = zfiles.read(f)
                #print(content)
                content = content.decode('utf8').split('\n') 
                content = [line.rstrip('\n') for line in content]
                list_output = create_dictionary(content)
                parfound=True
                break
    except KeyError:
        parfound=False

    if not parfound:
        print('ERROR: Did not find %s in zip file' % fname)
        return None
    return list_output

def create_new_content(file_url=None):
    '''
        create a new CMTSOLUTION file from json
    '''
    list_output = {}
    try:
        output=json.load(open(file_url))
        list_output=output['CMT']       
        list_output['event time'] = UTCDateTime(list_output['event time'])
    except KeyError:
        print('ERROR: Error reading json file %s' % file_url)
    return list_output

def load_local_content(file_url=None):
    '''
        reading CMTSOLUTION file from local path
    '''
    list_output = {}
    try:
        with open(file_url, "rt") as f:
            content = f.readlines()
            content = [line.rstrip('\n') for line in content]
        f.close()
        list_output = create_dictionary(content)
    except KeyError:
        print('ERROR: Error reading local file %s' % file_url)
    return list_output



class CreateSource(ProducerPE):
    def __init__(self):
        ProducerPE.__init__(self)

    def _process(self, data):
        file_url=data['file_url']
        out_url= data['out_url']
        pertubation=data['pertubation']
        UTM=data['UTM']
        type=data['type']
        index = data['index']
        
        if pertubation is None:
            print('Caution! You are using the default setting for location pertubation.')
            print('Set pertubation=[dMij,dZ,dX] for custom parameterization!')
        
        # key vector for json access
        MTe_notation = ['Mrr','Mtt','Mpp','Mrt','Mrp','Mtp','depth','latorUTM','longorUTM']
        if index != None:
            for MTi in range(index):
                self.write(
                    'output', {
                        'file_url' : file_url,
                        'out_url' : out_url,
                        'pertubation' : pertubation,
                        'UTM' : UTM,
                        'type' : type,
                        'MTe_notation': MTe_notation,
                        'MTi' : MTi }
                    )
        else:
            self.write(
                'output', {
                    'file_url' : file_url,
                    'out_url' : out_url,
                    'pertubation' : pertubation,
                    'UTM' : UTM,
                    'type' : type,
                    'MTe_notation': MTe_notation,
                    'MTi' : index }
                )

class CreateCMTSOLUTION(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)
        self.CMT = None
        self.file_url = None
        self.out_url = None
        self.perturbation = None
        self.UTM = None
        self.type = None
        self.MTe_notation = None
        self.MTi = None

    def _process(self, data):
        self.file_url = data['file_url']
        self.out_url =  data['out_url']
        self.pertubation = data['pertubation']
        self.UTM = data['UTM']
        self.type = data['type']
        self.MTe_notation = data['MTe_notation']
        self.MTi = data['MTi']
        self.CMT = self.read_file()
        self.control_pertubation_writer()

    def read_file(self):
        '''
            read in CMTSOLUTION information from different file types

        '''
        if self.type == 'local':
            CMT = load_local_content(file_url=self.file_url)
        if self.type == 'download':
            CMT = download_file_content(file_url=self.file_url,fname='CMTSOLUTION')
        if self.type == 'json':    
            CMT = create_new_content(file_url=self.file_url)
        return CMT
    
    
    def control_pertubation_writer(self):
        '''
            organize pertubations based on entry index
            None: create or pass initial file
            MTi: access and create pertubation based on selt.MTe_notation
        '''
        if self.MTi is None:
            true_MT, true_loc = self.get_true_model()
            MTe = np.append(true_MT, true_loc)
            self.write_file(MTe,'initial')    
            #os.rename("CMTSOLUTION", "CMTSOLUTION_"+key)    #magnoni: just to check the CMT creation
        else:
            MTe = self.var_elements()
            self.write_file(MTe,self.MTe_notation[self.MTi])    
            #os.rename("CMTSOLUTION", "CMTSOLUTION_"+self.MTe_notation[self.MTi])   
    
    def get_true_model(self):
        '''
            get initial MT elements and location from initial CMTSOLUTION 
        '''
        true_MT, true_loc = [], []
        for ind in self.MTe_notation[:6]:
            true_MT.append(self.CMT['event MT'][ind])
        for ind in self.MTe_notation[-3:]:
            true_loc.append(self.CMT['event location'][ind])
        return true_MT, true_loc
        
    def var_elements(self):
        '''
            create pertubation vector MTi contining MT elements and Location
            - for MT pertubations, source location is fixed on initial location
            - for location pertubation, non pertubat elements are fixed on initial settings
        '''
        # access true/initial synthetic source information
        true_MT, true_loc = self.get_true_model()
        
        # create MT elements pertubation vector
        MTe = np.zeros(9)
        MTi = self.MTi
        # simulate pertubations based on default parameterization (compare Pietro)
        if MTi < 6: # pertubation of MT elements
            if self.pertubation is None:
                print("pertubation is None")
                MTe[MTi] = 10**math.floor(math.log10(np.max(np.abs(np.asarray(true_MT)))))
            else:
                print("pertubation is something")
                if self.pertubation[0] == 'auto':
                    MTe[MTi] = 10**math.floor(math.log10(np.max(np.abs(np.asarray(true_MT)))))
                else:
                    MTe[MTi] = self.pertubation[0]
            MTe += np.append(np.zeros(6), true_loc)
        if MTi == 6: # pertubation in depth
            if self.pertubation is None:
                MTe[MTi] = true_loc[0]/5.
            else:
                MTe[MTi] = self.pertubation[1]
            MTe += np.append(true_MT, true_loc)
        if MTi > 6: # pertubation in latorUTM and longorUTM
            if self.pertubation is None:
                # case 1: location in UTM coordinates
                if self.UTM:
                    MTe[MTi] = 20*10**3 # 20 km ~ 0.18 degree
                    if MTi == 7: print('Caution! You are using the default setting for UTM coordinates.')
                else: # case 2: location in geographical coordinates
                    MTe[MTi] = 0.18
            else:
                MTe[MTi] = self.pertubation[2]
            MTe += np.append(true_MT, true_loc)            
        return MTe
    
    def write_file(self,MTe,key):
        '''
            write CMTSOLUTION file
        '''
        src_time = self.CMT['event time']
        with open(self.out_url+'CMTSOLUTION_'+key, "w") as f:
            f.write('PDE  %4i %2i %2i %2i %2i %5.2f %8.4f %9.4f %5.1f %.1f %.1f %s\n' 
                    % (src_time.year, src_time.month, src_time.day, src_time.hour,
                       src_time.minute, src_time.second, MTe[7], MTe[8], MTe[6], 
                       self.CMT['event magnitude']['mb'], self.CMT['event magnitude']['Ms'], self.CMT['event name']))
            f.write('event name:  %s\n' % self.CMT['event name'])
            f.write('time shift:    %9.4f\n'% self.CMT['time shift'])
            f.write('half duration: %9.4f\n'% self.CMT['half duration'])
            f.write('latorUTM:      %9.4f\n' % MTe[7])
            f.write('longorUTM:     %9.4f\n' % MTe[8])
            f.write('depth:         %9.4f\n' % MTe[6])
            f.write('Mrr:%19.6e\n' % MTe[0])  
            f.write('Mtt:%19.6e\n' % MTe[1])  
            f.write('Mpp:%19.6e\n' % MTe[2])  
            f.write('Mrt:%19.6e\n' % MTe[3])  
            f.write('Mrp:%19.6e\n' % MTe[4])  
            f.write('Mtp:%19.6e' % MTe[5])  
        f.close()
    
create_source_PE=CreateSource()
create_source_PE.name="create_source"
create_CMTSOLUTION_PE=CreateCMTSOLUTION()
create_CMTSOLUTION_PE.name="create_CMTSOLUTION"

graph = WorkflowGraph()
graph.connect(create_source_PE, "output", create_CMTSOLUTION_PE, "input")

