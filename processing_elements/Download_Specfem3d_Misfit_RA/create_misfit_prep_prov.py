# Run:
# MISFIT_PREP_CONFIG="/Users/rosa/VERCE/dispy/dispel4py/test/seismo/misfit/processing.json" python -m dispel4py.new.processor simple dispel4py.test.seismo.misfit.create_misfit_prep -f /Users/rosa/VERCE/dispy/dispel4py/test/seismo/misfit/misfit_input.jsn
#
# Expects an environment variable MISFIT_PREP_CONFIG with the JSON file that specifies the preprocessing graph.

import json
import os
import sys

import preprocessing_functions as mf
from preprocessing_functions import get_event_time, get_synthetics, sync_cut, rotate_data
from dispel4py.core import GenericPE
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.provenance import *
from seismo import SeismoSimpleFunctionPE, SeismoPE


class ReadDataPE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output_real')
        self._add_output('output_synt')
        self.counter = 0

    def _process(self, inputs):
        params = inputs['input']
        stations = params['station']
        networks = params['network']
        data_dir = params['data_dir']
        synt_dir = params['synt_dir']
        event_file = params['events']
        event_id = params['event_id']
        stations_dir = params['stations_dir']
        output_dir = params['output_dir']
        fe = 'v'
        if self.output_units == 'velocity':
            fe = 'v'
        elif self.output_units == 'displacement':
            fe = 'd'
        elif self.output_units == 'acceleration':
            fe = 'a'
        else:
            self.log('Did not recognise output units: %s' % output_units)
        quakeml = event_file
        for i in range(len(stations)):
            station = stations[i]
            network = networks[i]
            data_file = os.path.join(data_dir, network + "." + station + ".." + '?H?.mseed')
            #synt_file = os.path.join(synt_dir, network + "." + station + "." + '?X?.seed' + fe)
            ### in case we have the ascii synthetic traces, we have to comment the previous line, and uncomment the following one####### 
            synt_file = os.path.join(synt_dir, network + "." + station + "." + '?X?.sem' + fe)
            sxml = os.path.join(stations_dir, network + "." + station + ".xml")
            real_stream, sta, event = mf.read_stream(data_file, sxml=sxml,
                                                  event_file=quakeml,
                                                  event_id=event_id)
            synt_stream = get_synthetics(synt_file, 
                                         get_event_time(quakeml, event_id), station, network)
            data, synt = sync_cut(real_stream, synt_stream)
            self.write(
                'output_real', [data, { 
                    'station' : sta, 
                    'event' : event, 
                    'stationxml' : sxml, 
                    'quakeml' : quakeml, 
                    'output_dir' : output_dir }
                ])
            self.write(
                'output_synt', [synt, {
                    'station' : sta, 
                    'event' : event, 
                    'stationxml' : sxml, 
                    'quakeml' : quakeml, 
                    'output_dir' : output_dir }
                ])

class RotationPE(IterativePE):
    def __init__(self, tag):
        IterativePE.__init__(self)
        self.tag = tag

    def _process(self, data):
        stream, metadata = data
        output_dir = metadata['output_dir']
        stations = metadata['station']
        event = metadata['event']
        stats = stream[0].stats
        filename = "%s.%s.%s.png" % (
            stats['network'], stats['station'], self.tag)
        #stream.plot(outfile=os.path.join(output_dir, filename))
        stream = rotate_data(stream, stations, event)
        filename = "rotate-%s.%s.%s.png" % (
            stats['network'], stats['station'], self.tag)
        #stream.plot(outfile=os.path.join(output_dir, filename))
        return (stream, metadata)


class StoreStream(ConsumerPE):
    def __init__(self, tag):
        ConsumerPE.__init__(self)
        self.tag = tag
        self._add_output('output')

    def _process(self, data):
        filelist = {}
        stream, metadata = data
        output_dir = metadata['output_dir']
        for i in range(len(stream)):
            stats = stream[i].stats
            filename = os.path.join(output_dir, "%s.%s.%s.%s" % (
                stats['network'], stats['station'], stats['channel'], self.tag))
            stream[i].write(filename, format='MSEED')
            filelist[stats['channel']] = filename
            self.write('output',stream,location=filename)


class MisfitPreprocessingFunctionPE(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        stream, metadata = data
        result = self.compute_fn(stream, **self.params)
        
        if isinstance(result, dict) and '_d4p_prov' in result:
            if isinstance(self, (ProvenanceType)):
                result['_d4p_data']=result['_d4p_data'],metadata
                return result
            else:
                return result['_d4p_data'], metadata
        else:
            return result, metadata

def create_processing_chain(proc):
    processes = []
    for p in proc:
        fn_name = p['type']
        params = p['parameters']
        fn = getattr(mf, fn_name)
        processes.append((fn, params))
    return create_iterative_chain(processes, FunctionPE_class=MisfitPreprocessingFunctionPE)

with open(os.environ['MISFIT_PREP_CONFIG']) as f:
    proc = json.load(f)

real_preprocess = create_processing_chain(proc['data_processing'])
synt_preprocess = create_processing_chain(proc['synthetics_processing'])
    
graph = WorkflowGraph()
read = ReadDataPE()
read.name = 'data'
read.output_units = proc['output_units']
rotate_real = RotationPE('data')
rotate_synt = RotationPE('synth')
store_real = StoreStream('data')
store_synt = StoreStream('synth')
graph.connect(read, 'output_real', real_preprocess, 'input')
graph.connect(read, 'output_synt', synt_preprocess, 'input')
if proc['rotate_to_ZRT']:
    graph.connect(real_preprocess, 'output', rotate_real, 'input')
    graph.connect(synt_preprocess, 'output', rotate_synt, 'input')
    graph.connect(rotate_real, 'output', store_real, 'input')
    graph.connect(rotate_synt, 'output', store_synt, 'input')
else:
    graph.connect(real_preprocess, 'output', store_real, 'input')
    graph.connect(synt_preprocess, 'output', store_synt, 'input')
    
    
prov_config =  {
                    'provone:User': "fmagnoni", 
                    's-prov:description' : "provdemo demokritos",
                    's-prov:workflowName': "demo_epos",
                    's-prov:workflowType': "seis:preprocess",
                    's-prov:workflowId'  : "workflow process",
                    's-prov:save-mode'   : 'service'         ,
                    's-prov:WFExecutionInputs':  [{
                        "url": "",
                        "mime-type": "text/json",
                        "name": "input_data"
                         
                     },{"url": "/prov/workflow/export/"+os.environ['DOWNL_RUNID'],
                     "prov:type": "wfrun",
                     "mime-type": "application/octet-stream",
                     "name": "download_workflow",
                     "runid":os.environ['DOWNL_RUNID']}],
                    # defines the Provenance Types and Provenance Clusters for the Workflow Components                   
                    's-prov:componentsType' : 
                                       {'PE_taper': {'s-prov:type':(SeismoPE,),
                                                     's-prov:prov-cluster':'seis:Processor'},
                                        'PE_filter_bandpass': {'s-prov:type':(SeismoPE,),
                                                     's-prov:prov-cluster':'seis:Processor'},
                                        'StoreStream':    {'s-prov:prov-cluster':'seis:DataHandler',
                                                           's-prov:type':(SeismoPE,)},
                                        },
                    's-prov:sel-rules': None
                } 


ProvenanceType.REPOS_URL=os.environ['REPOS_URL']


#rid='JUP_PREPOC_'+getUniqueId()   
rid=os.environ['PREPOC_RUNID']             
                
configure_prov_run(graph,
                 provImpClass=(ProvenanceType,),
                 input=prov_config['s-prov:WFExecutionInputs'],
                 username=prov_config['provone:User'],
                 runId=rid,
                 description=prov_config['s-prov:description'],
                 workflowName=prov_config['s-prov:workflowName'],
                 workflowType=prov_config['s-prov:workflowType'],
                 workflowId=prov_config['s-prov:workflowId'],
                 save_mode=prov_config['s-prov:save-mode'],
                 componentsType=prov_config['s-prov:componentsType'],
                 sel_rules=prov_config['s-prov:sel-rules']

                    )
