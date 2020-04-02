import obspy
import json
import os
import sys
import networkx as nx
import glob,numpy
from obspy.core.event import read_events, ResourceIdentifier
import pyflex
import shutil #fm

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

def get_net_stat_ch(list_files_d, list_files_s):
    dlist=[]
    for d in list_files_d:
        net_d=d.split('/')[-1].split('.')[0]
        station_d=d.split('/')[-1].split('.')[1]
        channel_d=d.split('/')[-1].split('.')[2]
        for s in list_files_s:
            net_s=s.split('/')[-1].split('.')[0]
            station_s=s.split('/')[-1].split('.')[1]
            channel_s=s.split('/')[-1].split('.')[2]
            #NEEDED because we can have the obs seismogram but not the synt and viceversa
            if list(channel_d)[-1]!='E' and list(channel_d)[-1]!='N' and net_d==net_s and station_d==station_s and list(channel_d)[-1]==list(channel_s)[-1]:        
                dlist.append(net_d+'.'+station_d+'.'+channel_d+'.'+channel_s)
    dlist=numpy.unique(dlist)
    return dlist


class ProducerPE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')

    def _process(self, inputs):
        prep_output=inputs['prep_output']
        path_d=os.path.join(prep_output,'data')
        path_s=os.path.join(prep_output,'synth')
        
        json_file= inputs['json_input']
        #print("file json", json_file)
        
        input_data= inputs['input_data']
        path_id=os.path.join(input_data,'data')
        path_is=os.path.join(input_data,'synth')
        
        #
        if not os.path.exists(path_id):
            os.mkdir(path_id)

        if not os.path.exists(path_is):
            os.mkdir(path_is)
       
        pyflex_output= inputs['pyflex_output']
        #added here otherwise win files is duplicated
        
        pyflex_outdir= os.path.join(pyflex_output,'MEASURE') 
        if os.path.exists(pyflex_outdir):
            shutil.rmtree(pyflex_outdir, ignore_errors=True)
        #
        data=glob.glob(os.path.join(path_d,'*'))
        synt=glob.glob(os.path.join(path_s,'*'))
        #print(data)
        dlist=get_net_stat_ch(data,synt) #fm
        #print(dlist)
        networks=[]
        stations=[]
        channels_d=[]
        channels_s=[]
        for i,d in enumerate(dlist):
            if d in dlist:
                networks.append(d.split('.')[0])
                stations.append(d.split('.')[1])
                channels_d.append(d.split('.')[2]) #needed for the exact filename in the win file
                channels_s.append(d.split('.')[3]) #needed for the exact filename in the win file
        
        ### for pyflex later  
        event_file=input_data+'/events_info.xml'
        e=read_events(event_file)
        event_id=e.events[0].resource_id #quakeml with single event
        event = read_event(event_file, event_id)
        origin = event.preferred_origin() or event.origins[0] # fm added
        #print(origin.time) # fm added

        #read config parameters from json file        
        json_content = json.load(open(json_file))        
        UseCase = json_content['execution label']
        if UseCase == 'RA':
            print('Nothing to do here!')
        if UseCase == 'MT3D':
            min_period = json_content[UseCase]['pyflex_par']['min_period']
            #print("min_period", min_period)
            max_period= json_content[UseCase]['pyflex_par']['max_period']
            stalta_waterlevel= json_content[UseCase]['pyflex_par']['stalta_waterlevel']
            tshift_acceptance_level= json_content[UseCase]['pyflex_par']['tshift_acceptance_level']
            dlna_acceptance_level= json_content[UseCase]['pyflex_par']['dlna_acceptance_level']
            s2n_limit= json_content[UseCase]['pyflex_par']['s2n_limit']
            cc_acceptance_level= json_content[UseCase]['pyflex_par']['cc_acceptance_level']
            c_0= json_content[UseCase]['pyflex_par']['c_0']
            c_1= json_content[UseCase]['pyflex_par']['c_1']
            c_2= json_content[UseCase]['pyflex_par']['c_2']
            c_3a= json_content[UseCase]['pyflex_par']['c_3a']
            c_3b= json_content[UseCase]['pyflex_par']['c_3b']
            c_4a= json_content[UseCase]['pyflex_par']['c_4a']
            c_4b= json_content[UseCase]['pyflex_par']['c_4b']
            check_global_data_quality= json_content[UseCase]['pyflex_par']['check_global_data_quality']
            snr_integrate_base= json_content[UseCase]['pyflex_par']['snr_integrate_base']
            snr_max_base= json_content[UseCase]['pyflex_par']['snr_max_base']
            max_time_before_first_arrival= json_content[UseCase]['pyflex_par']['max_time_before_first_arrival']
            earth_model= json_content[UseCase]['pyflex_par']['earth_model']
            noise_start_index= json_content[UseCase]['pyflex_par']['noise_start_index']
            noise_end_index= json_content[UseCase]['pyflex_par']['noise_end_index']
            signal_start_index= json_content[UseCase]['pyflex_par']['signal_start_index']
            signal_end_index= json_content[UseCase]['pyflex_par']['signal_end_index']
            resolution_strategy= json_content[UseCase]['pyflex_par']['resolution_strategy']
            window_signal_to_noise_type= json_content[UseCase]['pyflex_par']['window_signal_to_noise_type']
        
        config = pyflex.Config(
            min_period=min_period, max_period=max_period,
            stalta_waterlevel=stalta_waterlevel, tshift_acceptance_level=tshift_acceptance_level,
            dlna_acceptance_level=dlna_acceptance_level, s2n_limit=s2n_limit,cc_acceptance_level=cc_acceptance_level,
            c_0=c_0, c_1=c_1, c_2=c_2, c_3a=c_3a, c_3b=c_3b, c_4a=c_4a, c_4b=c_4b,
            check_global_data_quality=check_global_data_quality,snr_integrate_base=snr_integrate_base,
            snr_max_base=snr_max_base, max_time_before_first_arrival=max_time_before_first_arrival,earth_model=earth_model,noise_start_index=noise_start_index, noise_end_index=noise_end_index,
            signal_start_index=signal_start_index, signal_end_index=signal_end_index,resolution_strategy=resolution_strategy,
            window_signal_to_noise_type=window_signal_to_noise_type)
        
        
        ##getting unique values of stations, stations' contains three times the name of the same station (e.g. ARRO for R,T,Z components). 
        unique_stations=list(set(stations))
        ## creating a dictionary with the stations as keys, and 0 as the default value for each of them.  
        interpolation_flags = dict.fromkeys(unique_stations, 0)
        num_pairs=len(stations)
        for i in range(len(stations)):
            st = stations[i]
            net = networks[i]
            chl_d = channels_d[i]
            chl_s = channels_s[i] 
            comp = chl_d[-1]

            ## checking that the interpolation_flags vale for this particular station is 0 - It should enter here only once per station. 
            if interpolation_flags[stations[i]] == 0:
                ## This interpolation variable, will indicate to the next PE, that the interpolation for this station has to be done. It will do this just once per station. 
                interpolation = 1
                self.write('output',[interpolation, path_d, path_s, path_id, path_is, net, st, chl_d, chl_s, event, origin, input_data, pyflex_outdir, num_pairs, config])
                
                ##set the flag for this particular station to 1. 
                interpolation_flags[stations[i]] = 1
            ## For the rest of the cases in which interpolation_flags vale for this particular station is 1 - It should enter here more than once per station
            else:
                ## This interpolation variable, will indicate to the next PE, that the interpolation for this station doesnt need to be done. 
                interpolation = 0
                self.write('output',[interpolation, path_d, path_s, path_id, path_is, net, st, chl_d, chl_s, event, origin, input_data, pyflex_outdir, num_pairs, config])
            

class InterpolatePE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')

    def _process(self, inputs):

        interpolation, path_d, path_s, path_id, path_is,  net, st, chl_d, chl_s, event, origin, input_data, pyflex_outdir, num_pairs, config = inputs['input']
        #checking if the interpolation variable is 1 - in that case, I have to interpolate this station. 

        if interpolation == 1:
            # I should have the next print just once per station
            print("Sanity check - interpolating data for station %s" %st)

            data=obspy.read(path_d+'/'+net+'.'+ st + '.???.data')
            synth=obspy.read(path_s+'/'+net+'.'+ st + '.???.synth')
            print("data", data)
            print("synth", synth)        
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
            
            ##check interpolation
            data_i=obspy.read(path_id+'/'+net+'.'+ st + '.???.data')
            synth_i=obspy.read(path_is+'/'+net+'.'+ st + '.???.synth')
            print("data interp", data_i)
            print("synth interp", synth_i)                
            ##

        data_dir=path_id+'/'+net+'.'+st+'.'+chl_d+'.data'
        synth_dir=path_is+'/'+net+'.'+st+'.'+chl_s+'.synth'
        self.write('output',[synth_dir, data_dir, net, st, chl_d, chl_s, event, origin, input_data, pyflex_outdir, num_pairs, config])


class PyflexPE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')

    def _process(self, inputs):
        synth_dir, obs_dir, net, st, chl_d, chl_s, event, origin, input_data, pyflex_outdir, num_pairs, config = inputs['input']        
        
        if not os.path.exists(pyflex_outdir):
            os.mkdir(pyflex_outdir)
        synth_data = obspy.read(synth_dir)
        print('synth_data', synth_data)
        obs_data = obspy.read(obs_dir)
        print('obs_data', obs_data)
        
        plot_filename = net+'.'+st+'.'+chl_s+'.png'
        win_filename = net+'.'+st+'.'+chl_s #new output files

        station_file = input_data+"/stations/"+net+'.'+st+'.xml'
        station = obspy.read_inventory(station_file, format="STATIONXML")
        
        windows = pyflex.select_windows(obs_data, synth_data, config, event=event, station=station, plot=True, plot_filename= pyflex_outdir+'/'+plot_filename, windows_filename=pyflex_outdir+'/'+win_filename)
        self.write('output',[synth_dir, obs_dir, origin, pyflex_outdir, num_pairs, windows])

class UpdateFilePE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        #self._add_input('input')
        self._add_input('input', grouping="global")
        self._add_output('output')
        self.win_count=0
        self.pair_count=1

       
    def _process(self, inputs):
        synth_dir, obs_dir, origin, pyflex_outdir, num_pairs, windows = inputs['input']
        print("-------> Sanity Check: Num pairs %s - Pair_count %s" %(num_pairs, self.pair_count))
        name_output= pyflex_outdir+'/pyflex_win.txt'
        ##'append' otherwise doesn't keep all the windows
        file_output_pyflex=open(name_output,"a")
                
        ##to be more generic
        data_name_f=obs_dir.split('/')[-2]
        data_name_tr=obs_dir.split('/')[-1]
        synth_name_f=synth_dir.split('/')[-2]
        synth_name_tr=synth_dir.split('/')[-1]


        synth_data = obspy.read(synth_dir)
        obs_data = obspy.read(obs_dir)
        
        if len(windows)>0:
            self.win_count+=1
            
            ##write win file without offset            
            file_output_pyflex.write('./'+data_name_f +'/' + data_name_tr+'\n')
            file_output_pyflex.write('./'+synth_name_f+'/' + synth_name_tr+'\n')
            file_output_pyflex.write(str(len(windows))+'\n')
            for win in range(0,len(windows)):
                file_output_pyflex.write(str(windows[win].relative_starttime)+'   '+str(windows[win].relative_endtime)+'\n')                

        #NEEDED because the final win file should start with the total number of couples data-synth with wins
        if self.pair_count == num_pairs:
            with open(name_output, 'r') as original: 
                 win_list = original.read()
            with open(name_output, 'w') as modified: 
                 modified.write(str(self.win_count)+'\n' + win_list)
        self.pair_count += 1
        file_output_pyflex.close()
        

graph = WorkflowGraph()
producer = ProducerPE()
producer.name = 'producer'
interpolate = InterpolatePE()
updateFile=UpdateFilePE()
updateFile.numprocesses = 1
pyflexPE = PyflexPE()
graph.connect(producer, 'output', interpolate, 'input')
graph.connect(interpolate, 'output', pyflexPE, 'input')
updateFile.inputconnections['input']['grouping'] = 'global'
graph.connect(pyflexPE, 'output', updateFile, 'input')
