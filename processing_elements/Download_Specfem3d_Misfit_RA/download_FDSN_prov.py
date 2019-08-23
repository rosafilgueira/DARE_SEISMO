from dispel4py.base import SimpleFunctionPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE
from dispel4py.provenance import *
from seismo import SeismoSimpleFunctionPE, SeismoPE, PlotPE

import obspy
from obspy.core import read
from obspy.clients.fdsn.header import URL_MAPPINGS

import os
import sys
import pickle
import xml.etree.ElementTree as ET

from domain import RectangularDomain, CircularDomain 
from download_helpers import Restrictions, DownloadHelper


def waveform_reader(data):
    filename = data
    st = read(filename)
    return st


def stationxml_reader(data):
    filename = data
    tree = ET.parse(filename)
    root = tree.getroot()
    scode = ''
    ncode = ''
    n = root.find('{http://www.fdsn.org/xml/station/1}Network')
    ncode = n.get('code')
    s = n.find('{http://www.fdsn.org/xml/station/1}Station')
    scode = s.get('code')
    return data


def plot_stream(stream, output_dir, source, tag):
    stats = stream[0].stats
    filename = source + "-%s.%s.%s.%s.png" % (
        stats['network'], stats['station'], stats['channel'], tag)

    path = os.environ['STAGED_DATA'] + '/' + output_dir

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            pass
    dest = os.path.join(path, filename)
    stream.plot(outfile=dest)
    #return stream
    prov = {'location': "file://" + socket.gethostname() + "/" + dest, 'format': 'image/png',
                'metadata': {'prov:type': tag,'station':stats['station'],'channel':stats['channel'],'network':stats['network']}}
    return {'_d4p_prov': prov, '_d4p_data': stream}
    


# Rectangular domain containing parts of southern Germany.
def download_data(data,add_end,add_start):    #fm
    # A fix for globe to access the data values if the whole data gets assigned to the property input
    if 'input' in data:
        data = data['input']

    # solverType is used to differentiate between globe and cartesian runs
    # solverType,networks and stations are initially defined as None in order to support the reusability of older cartesian runs
    solverType = None
    networks=None
    stations=None

    if 'solverType' in data:
        solverType = data['solverType'];

    if 'networks' in data:
        networks = data['networks'];

    if 'stations' in data:
        stations = data['stations'];

    # if solverType == "SPECFEM3D_GLOBE":
    #     #endtime = obspy.UTCDateTime(data['ORIGIN_TIME']) + (float(data['RECORD_LENGTH_IN_MINUTES']) * 60) + 300
    #     endtime = obspy.UTCDateTime(data['ORIGIN_TIME']) + (float(data['RECORD_LENGTH_IN_MINUTES']) * 60) + add_end   #fm
    # else:
    #     #endtime = obspy.UTCDateTime(data['ORIGIN_TIME']) + float(data['DT']) * int(data['NSTEP']) + 300
    #     endtime = obspy.UTCDateTime(data['ORIGIN_TIME']) + float(data['DT']) * int(data['NSTEP']) + add_end   #fm

    endtime = obspy.UTCDateTime(data['ORIGIN_TIME']) + (float(data['RECORD_LENGTH_IN_MINUTES']) * 60) + add_end   #fm        
    print("%s\n" % solverType)

    if solverType == "SPECFEM3D_GLOBE" and (float(data['minlongitude']) < -180 or float(data['maxlongitude']) > 180):
        domain = CircularDomain(
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            minradius=float(data['minradius']),
            maxradius=float(data['maxradius']))

    else:
        domain = RectangularDomain(
            minlatitude=float(data['minlatitude']),
            maxlatitude=float(data['maxlatitude']),
            minlongitude=float(data['minlongitude']),
            maxlongitude=float(data['maxlongitude']))

    restrictions = Restrictions(
        # Get data for a whole yearlatitude.
        starttime=obspy.UTCDateTime(data['ORIGIN_TIME']) - add_start,     #fm 
        endtime=endtime,
        # Considering the enormous amount of data associated with continuous
        # requests, you might want to limit the data based on SEED identifiers.
        # If the location code is specified, the location priority list is not
        # used; the same is true for the channel argument and priority list.
        network=networks, station=stations, location=None, channel=None,
        # The typical use case for such a data set are noise correlations where
        # gaps are dealt with at a later stage.
        reject_channels_with_gaps=True,
        # Same is true with the minimum length. Any data during a day might be
        # useful.
        minimum_length=0.99,
        # Guard against the same station having different names.
        minimum_interstation_distance_in_m=data[
            'minimum_interstation_distance_in_m'],
        channel_priorities=data['channel_priorities'],
        location_priorities=data['location_priorities']

    )
    print("TIME WIND: %s" % str((str(restrictions.starttime), str(restrictions.endtime))))
    dlh = DownloadHelper(providers=["IRIS"]) if solverType == "SPECFEM3D_GLOBE" else DownloadHelper()

    mseed_path = os.environ['STAGED_DATA'] + "/" + data['mseed_path']
    stationxml_path = os.environ['STAGED_DATA'] + "/" + data['stationxml_path']
    if not os.path.exists(stationxml_path):
        try:
            os.makedirs(stationxml_path)
        except:
            pass

    report = dlh.download(
        domain=domain, restrictions=restrictions,
        mseed_path=mseed_path,
        stationxml_path=stationxml_path)

    download_report = []
    # Bit of a hack!
    URL_MAPPINGS["INGV"] = "http://webservices.rm.ingv.it"
    for r in report:
        for station in r["data"]:
            download_report.append({"provider": r["client"],
                                    "provider_url": URL_MAPPINGS[r["client"]],
                                    "station": "%s.%s" % (station.network, station.station)})

    #return os.environ['STAGED_DATA'] + "/" + data['mseed_path'], os.environ['STAGED_DATA'] + "/" + data['stationxml_path']
    prov = {'location': ["file://" + socket.gethostname() + "/" + os.environ['STAGED_DATA'] + "/" + data['mseed_path'],
                             "file://" + socket.gethostname() + "/" + os.environ['STAGED_DATA'] + "/" + data[
                                 'stationxml_path']], 'format': 'multipart/mixed', 'metadata': download_report}
    return {'_d4p_prov': prov, '_d4p_data': [os.environ['STAGED_DATA'] + "/" + data['mseed_path'],
                                        os.environ['STAGED_DATA'] + "/" + data['stationxml_path']]}


class WatchDirectory(IterativePE):
    def __init__(self, index):
        IterativePE.__init__(self)
        self.index = index

    def _process(self, inputs):

        directory = inputs
        print("DIRECOTRY:%s " % str(directory))
        for dir_entry in os.listdir(directory[self.index]):

            dir_entry_path = os.path.join(directory[self.index], dir_entry)
            if os.path.isfile(dir_entry_path):
                self.write('output', dir_entry_path)



downloadPE = SimpleFunctionPE(download_data,{"add_end": 600, "add_start": 300})    #fm 
downloadPE.name = "downloadPE"
watcher = WatchDirectory(0)
watcher_xml = WatchDirectory(1)
waveformr = SimpleFunctionPE(waveform_reader)
xmlr = SimpleFunctionPE(stationxml_reader)

processes = [waveform_reader,
             (plot_stream, {"source": "waveform_reader", "output_dir": "./output-images", "tag": "observed-image"})]

chain = create_iterative_chain(processes, FunctionPE_class=SimpleFunctionPE)

graph = WorkflowGraph()
graph.connect(downloadPE, 'output', watcher, "input")
graph.connect(downloadPE, 'output', watcher_xml, "input")
graph.connect(watcher, 'output', chain, "input")
graph.connect(watcher_xml, 'output', xmlr, "input")

prov_config =  {
                    'provone:User': "fmagnoni", 
                    's-prov:description' : "download data",
                    's-prov:workflowName': "demo_epos",
                    's-prov:workflowType': "seis:preprocess",
                    's-prov:workflowId'  : "workflow process",
                    's-prov:save-mode'   : 'service'         ,
                    's-prov:WFExecutionInputs':  [{
                        "url": "",
                        "mime-type": "text/json",
                        "name": "input_data"
                         
                     }],
    
                    # defines the Provenance Types and Provenance Clusters for the Workflow Components
                    's-prov:componentsType' : 
                                       {'PE_waveform_reader': {'s-prov:type':(SeismoPE,),
                                                     's-prov:prov-cluster':'seis:Reader'},
                                        
                                        },
                                        
                    's-prov:sel-rules': None
                } 
                
ProvenanceType.REPOS_URL=os.environ['REPOS_URL']

#rid='JUP_DOWNLOAD_'+getUniqueId()
rid=os.environ['DOWNL_RUNID']

# Finally, provenance enhanced graph is prepared:
 
#Initialise provenance storage to service:
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
                 #sel_rules=prov_config['s-prov:sel-rules']
                  
                )
                

