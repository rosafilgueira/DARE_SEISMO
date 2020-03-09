import obspy
import json
import os
import sys
import networkx as nx
import glob,numpy
from obspy.core.event import read_events, ResourceIdentifier
import pyflex
from pyflex import WindowSelector

import logging
logger=logging.getLogger('pyflex')
logger.setLevel(logging.DEBUG)

from dispel4py.core import GenericPE
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.workflow_graph import write_image
from obspy.core.event import read_events
from PIL import Image


def read_event(event_file, event_id):
    events = read_events(event_file)
    event = None
    resource_id = ResourceIdentifier(event_id)
    for evt in events:
        if evt.resource_id == resource_id:
           event = evt
    if event is None:
        event = events[0]
    return event

def get_net_station(list_files):
    dlist=[]
    for d in list_files:
        net=d.split('/')[-1].split('.')[0]
        station=d.split('/')[-1].split('.')[1]
        dlist.append(net+'.'+station)
    dlist=numpy.unique(dlist)
    return dlist


class InterpolatePE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')

    def _process(self, inputs):
        OUTPUT_DATA=os.environ['OUTPUT_DATA']
        path_d=os.path.join(OUTPUT_DATA,'data')
        path_s=os.path.join(OUTPUT_DATA,'synth')
        
        INTERPOLATED_DATA=os.environ['INTERPOLATED_DATA']
        path_id=os.path.join(INTERPOLATED_DATA,'data_pe')
        path_is=os.path.join(INTERPOLATED_DATA,'synth_pe')
        
        data=glob.glob(os.path.join(path_d,'*'))
        synt=glob.glob(os.path.join(path_s,'*'))
        dlist=get_net_station(data)
        networks=[]
        stations=[]
        for i,d in enumerate(dlist):
            if d in dlist:
                networks.append(d.split('.')[0])
                stations.append(d.split('.')[1])
        
        ### for pyflex later  
        event_file=INTERPOLATED_DATA+'/events_info.xml'
        e=read_events(event_file)
        event_id=e.events[0].resource_id #quakeml with single event
        event = read_event(event_file, event_id)
        #####
        for i in range(len(stations)):
            st = stations[i]
            net = networks[i]
           
            component_data='??R'
            component_synth='HXR'
            data=obspy.read(path_d+'/'+net+'.'+ st + '.' + component_data +'.data')
            synth=obspy.read(path_s+'/'+net+'.'+ st + '.' + component_synth +'.synth')
            
            sampling_rate = min([tr.stats.sampling_rate for tr in (data + synth)])
            starttime = max([tr.stats.starttime for tr in (data + synth)])
            endtime = min([tr.stats.endtime for tr in (data + synth)])
            npts = int((endtime - starttime) * sampling_rate)

            synth.interpolate(sampling_rate=sampling_rate, method="cubic", starttime=starttime, npts=npts)
            data.interpolate(sampling_rate=sampling_rate, method="cubic", starttime=starttime, npts=npts)

            for trace in synth:
                trace.write(path_is+"/"+str(trace.stats.network+'.'+trace.stats.station+'.'+trace.stats.channel)+".synth",format='sac') 

            for trace in data:
                trace.write(path_id+"/"+str(trace.stats.network+'.'+trace.stats.station+'.'+trace.stats.channel)+".data",format='sac') 
           
            data=obspy.read(path_id+'/'+net+'.'+ st + '.' + component_data +'.data')
            synth=obspy.read(path_is+'/'+net+'.'+ st + '.' + component_synth +'.synth')
            self.write('output',[synth, data, net, st, component_data, component_synth, event])
            

class PyflexPE(GenericPE):
    def __init__(self, configuration):
        GenericPE.__init__(self)
        self._add_input ('input')
        self._add_output('image')
        self._add_output('window')
        self.configuration=configuration

    def _process(self, inputs):

        path_output=os.environ['PYFLEX_RESULTS']
        pyflex_outdir= os.path.join(path_output,'MEASURE')
        name_output=path_output+'/pyflex_win.txt'
        file_output_pyflex=open(name_output,"w")

        INTERPOLATED_DATA=os.environ['INTERPOLATED_DATA']

        data_name_f='/data'
        synth_name_f='/synth'

        synth_data, obs_data, net, st, component_data, component_synth, event = inputs['input']
        if list(component_data)[-1]!='E' and list(component_data)[-1]!='N' and list(component_data)[-1]==list(component_synth)[-1]: 
            plot_filename = net+'.'+st+'.'+component_synth+'.png'

            station_file = INTERPOLATED_DATA+"/stations/"+net+'.'+st+'.xml'
            station = obspy.read_inventory(station_file, format="STATIONXML")
            windows = pyflex.select_windows(obs_data, synth_data, config, event=event, station=station, plot=True, plot_filename= pyflex_outdir+'/'+plot_filename)
            if len(windows)>0:
                offset=-synth_data[0].stats.sac[u'b']
                file_output_pyflex.write('.'+data_name_f +'/' + net+'.'+st+'.'+component_data+'\n')
                file_output_pyflex.write('.'+synth_name_f+'/' + net+'.'+st+'.'+component_synth+'\n')
                file_output_pyflex.write(str(len(windows))+'\n')
                for win in range(0,len(windows)):
                    file_output_pyflex.write(str(windows[win].relative_starttime-offset)+'   '+str(windows[win].relative_endtime-offset)+'\n')
            
                
                    
        file_output_pyflex.close()

#config = pyflex.Config(
#    min_period=20.0, max_period=50.0,
#    stalta_waterlevel=0.07, tshift_acceptance_level=10.0,
#    dlna_acceptance_level=1.3, s2n_limit=4.0,cc_acceptance_level=0.68,
#    c_0=1.0, c_1=1.5, c_2=0.0, c_3a=4.0, c_3b=2.5, c_4a=2.0, c_4b=6.0,
#    check_global_data_quality=False,snr_integrate_base=2.5,
#                 snr_max_base=3.5, max_time_before_first_arrival=5,earth_model="iasp91",noise_start_index=0, noise_end_index=None,
#                 signal_start_index=None, signal_end_index=-1,resolution_strategy="interval_scheduling",
#    window_signal_to_noise_type='energy')


config = pyflex.Config(
    min_period=0.5, max_period=10.0,
    stalta_waterlevel=0.07, tshift_acceptance_level=5.0,
    dlna_acceptance_level=1.3, s2n_limit=4.0,cc_acceptance_level=0.68,
    c_0=1.0, c_1=1.5, c_2=0.0, c_3a=4.0, c_3b=2.5, c_4a=2.0, c_4b=6.0,
    check_global_data_quality=False,snr_integrate_base=2.5,
                 snr_max_base=3.5, max_time_before_first_arrival=5,earth_model="iasp91",noise_start_index=0, noise_end_index=None,
                 signal_start_index=None, signal_end_index=-1,resolution_strategy="interval_scheduling",
    window_signal_to_noise_type='energy')

graph = WorkflowGraph()
interpolate = InterpolatePE()
interpolate.name = 'interpolate'
pyflexPE = PyflexPE(config)

graph.connect(interpolate, 'output', pyflexPE, 'input')



