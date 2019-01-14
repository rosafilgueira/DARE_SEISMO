'''
Execution:
dispel4py simple dispel4py_RA.pgm_story_comparative.py -d '{"streamProducer": [ {"input": ["GroundMotion_IV.MA9..HHR.START.OTLOC.SAC.20.50.real.json", "GroundMotion_IV.MA9.HXR.semv.sac.20.50.synt.json"]} ] }'
'''

from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph

from obspy.core.stream import read
from obspy.signal.invsim import corn_freq_2_paz, simulate_seismometer
from obspy.signal import differentiate_and_integrate as di

import math
import numpy as np
import os
import json


def comp(real_param , synt_param):
    result_diff = float(real_param) - float(synt_param)
    result_perc = (float(real_param) - float(synt_param))/float(real_param)
    return result_diff, result_perc


class StreamProducer(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)    

    def _process(self, input):
        input_real, input_synth = input
        with open(input_real) as f:
           data_real = json.load(f)
        with open(input_synth) as f:
           data_synth = json.load(f)
        self.write('output', [data_real, data_synth])                


class Comparative(IterativePE):
    def __init__(self):
        IterativePE.__init__(self)
       
    def _process(self, s_data):
        data_real, data_synth = s_data
        results={}
        for param in ['pgd', 'pgv', 'pga', 'dmp_spec_acc']:
            param_diff, param_perc = comp(data_real["GroundMotion"][param], data_synth["GroundMotion"][param])
            results[param]={param_diff, param_perc}
        results["ty"]=data_real["GroundMotion"]["ty"]
        results["stream_synt"]=data_real["GroundMotion"]["stream"]
        results["stream_real"]=data_real["GroundMotion"]["stream"]
        results["p_norm"]=data_real["GroundMotion"]["p_norm"]
        self.write('output', [results])    


streamProducer=StreamProducer()
streamProducer.name='streamProducer'
compData=Comparative()


graph = WorkflowGraph()
graph.connect(streamProducer, 'output', compData,'input')

