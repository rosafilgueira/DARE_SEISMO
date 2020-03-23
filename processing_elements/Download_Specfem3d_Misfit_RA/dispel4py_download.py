from dispel4py.base import SimpleFunctionPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE, ProducerPE
from dispel4py.provenance import *
from dispel4py.workflow_graph import write_image

import zipfile
import requests,json
import io
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sys,os
path = "/home/mpiuser/sfs/d4p"
path = os.path.join(path, os.environ["RUN_DIR"])
os.system('wget -P {} https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/domain.py'.format(path))
os.system('wget -P {} https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/download_helpers.py'.format(path))
os.system('wget -P {} https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/utils.py'.format(path))
os.system('wget -P {} https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/seismo.py'.format(path))
sys.path.append(os.environ['PWD'])
os.environ['STAGED_DATA'] = '/home/mpiuser/sfs/specfem/Th1s4sY0urT0k3Nn_demo_data'
os.environ['DOWNL_RUNID'] = os.environ['RUN_ID']
os.environ['REPOS_URL'] = 'http://'+os.getenv('SPROV_SERVICE_HOST')+':'+os.getenv('SPROV_SERVICE_PORT')+'/workflowexecutions/insert'
import re
import numpy

import obspy
from obspy.core import read
from obspy.clients.fdsn.header import URL_MAPPINGS

import pickle
import xml.etree.ElementTree as ET

from seismo import SeismoSimpleFunctionPE, SeismoPE, PlotPE
from domain import RectangularDomain, CircularDomain 
from download_helpers import Restrictions, DownloadHelper


def get_file_content(file_url=None,directory=None,
                     fname=None,archive=False):
    if archive:
        try:
            try:
                response = requests.get(file_url)
                zfiles=zipfile.ZipFile(io.BytesIO(response.content))
            except:
                zfiles=zipfile.ZipFile(file_url)
            listfile = zfiles.namelist()
        except:
             print('ERROR: Error reading zip file %s' % file_url)
             
        list_output = []
        if type(fname!=list):
            fname=list(fname)
        for name in fname:
            try:
                parfound=False
                for f in listfile:
                    if name in f:
                        ifile = zfiles.read(f)
                        ifile = ifile.decode('utf8')
                        if ('.json' in name) or ('.jsn' in name): 
                            ifile=json.loads(ifile)
                        list_output.append(ifile)
                        parfound=True
                        break
            except KeyError:
                parfound=False

        if not parfound:
            print('ERROR: Did not find %s in zip file' % fname)
            return None
    elif directory:
        if type(fname!=list):
            fname=list(fname)
        for name in fname:
            try:
                print(os.path.join(directory,name))
                f=open(os.path.join(directory,name),'r')
                ifile=f.read()
                ifile = ifile.decode('utf8')
                if ('.json' in name) or ('.jsn' in name):
                    ifile=json.loads(ifile)
                list_output.append(ifile)
            except:
                print('ERROR: Error reading %s file in %s' % (name,directory))
    elif ('.json' in fname) or ('.jsn' in fname):
        try:
            try:
                response = requests.get(file_url)
                ifile=response.json()
            except:
                f=open(file_url,'r')
                ifile=json.loads(f.read())
                f.close()
        except:
             print('ERROR: Error reading json file %s' % file_url)
        ifile = ifile.decode('utf8')
        if json_format: ifile=json.loads(ifile)
        list_output=[ifile]
    return list_output

def get_parameter(parameter=None,string=None,reg='\s+=([\s\d\.]+)'):
    if parameter is None:
        print('Parameter missed, ex: parameter="NPROC"')
        return None
    elif string is None:
        print('file string missing')
    txt=parameter+reg
    p=re.findall(txt, string,re.MULTILINE)
    if len(p) > 0:
        return p[0]
    else:
        return None

def create_event_time(cmtsolution):
    regex = r"PDE\s[\d\.\s]+"
    event_time=re.findall(regex, cmtsolution,re.MULTILINE)[0].split()[1:7]
    return '-'.join(x.zfill(2) for x in event_time[:3]) +\
            'T' +\
            ':'.join(x.zfill(2) for x in event_time[3:-1]) +':'+\
            '.'.join(x.zfill(2) for x in event_time[-1].split('.'))

def get_coordlimits(mesh):
    d = numpy.fromstring(mesh, sep=' ')
    data = d[1:].reshape(int(d[0]), 4)
    return data[:, 1].min(), data[:, 1].max(),\
        data[:, 2].min(), data[:, 2].max(),\
        data[:, 3].min(), data[:, 3].max()

def get_mesh_geolimits(lim,epsg):
    import pyproj
    wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
    meshcoordinate=pyproj.Proj("+init="+epsg)
    pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])
    longitude_min=max(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])[0],
                  pyproj.transform(meshcoordinate, wgs84, lim[0], lim[3])[0])
    longitude_max=min(pyproj.transform(meshcoordinate, wgs84, lim[1], lim[2])[0],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[3])[0])
    latitude_min=max(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[2])[1],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[2])[1])
    latitude_max=min(pyproj.transform(meshcoordinate, wgs84, lim[0], lim[3])[1],
                  pyproj.transform(meshcoordinate, wgs84, lim[1], lim[3])[1])
    return longitude_min,longitude_max,latitude_min,latitude_max


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
    prov = {'location': "file://" + socket.gethostname() + "/" + dest, 'format': 'image/png',
                'metadata': {'prov:type': tag,'station':stats['station'],'channel':stats['channel'],'network':stats['network']}}
    return {'_d4p_prov': prov, '_d4p_data': stream}


# Rectangular domain containing parts of southern Germany.
def download_data(data,add_end,add_start):    #fm
    # A fix for globe to access the data values if the whole data gets assigned to the property input
    print("ENTROOOOOOO data:%s:" %data)
    data=data['downloadPE'][0]['input']
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

    prov = {'location': ["file://" + socket.gethostname() + "/" + os.environ['STAGED_DATA'] + "/" + data['mseed_path'],
                             "file://" + socket.gethostname() + "/" + os.environ['STAGED_DATA'] + "/" + data[
                                 'stationxml_path']], 'format': 'multipart/mixed', 'metadata': download_report}
    return {'_d4p_prov': prov, '_d4p_data': [os.environ['STAGED_DATA'] + "/" + data['mseed_path'],
                                        os.environ['STAGED_DATA'] + "/" + data['stationxml_path']]}


class ReadSpecfem3d(ProducerPE):
    def __init__(self):
        ProducerPE.__init__(self)

    def _process(self, data):
        print(data)
        data_url=data['specfem3d_data_url']
        cmtsolution,parfile,infopar,meshfile=get_file_content(file_url=data_url,
                                                              fname=['CMTSOLUTION','Par_file','Info.json','nodes_coords_file'],
                                                              archive=True)
        NPROC=int(get_parameter('NPROC',parfile))
        print(NPROC)
        dt=float(get_parameter('DT',parfile))
        nstep=int(get_parameter('NSTEP',parfile))
        print(dt,nstep)
        try:
            RECORD_LENGTH_IN_MINUTES=float(get_parameter('RECORD_LENGTH_IN_MINUTES',parfile))
        except:
            RECORD_LENGTH_IN_MINUTES=dt*nstep/60.

        ETIME=create_event_time(cmtsolution)
        print(ETIME)
        lim=get_coordlimits(meshfile)
        print(RECORD_LENGTH_IN_MINUTES)
        print(lim)
        epsg=infopar['Coordinatesystem']['EPSG']
        longitude_min,longitude_max,latitude_min,latitude_max=get_mesh_geolimits(lim,epsg)
        xmin,xmax,ymin,ymax,zmin,zmax=lim


        d={
                "simulationRunId": None,
                "runId": None,
                "nproc": NPROC,
                "downloadPE": [
                    {
                    "input": {
                        "minimum_interstation_distance_in_m": 100,
                        "channel_priorities": ["BH[E,N,Z]","EH[E,N,Z]"],
                        "location_priorities": ["","00","10"],
                        "mseed_path": "./data",
                        "stationxml_path": "./stations",
                        "RECORD_LENGTH_IN_MINUTES": RECORD_LENGTH_IN_MINUTES,
                        "ORIGIN_TIME": ETIME,
                        "minlatitude": latitude_min,
                        "maxlatitude": latitude_max,
                        "minlongitude": longitude_min,
                        "maxlongitude": longitude_max
                        }
                    }
                ]
        }
        if 'output' in data:
            filename = data['output']
            with open(filename, "w") as write_file:
                json.dump(d, write_file)
        
        self.write('output',d,metadata=d)


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



read_stream = ReadSpecfem3d()
read_stream.name="ReadSpecfem3d"
downloadPE = SimpleFunctionPE(download_data,{"add_end": 300, "add_start": 300})    #fm
downloadPE.name = "downloadPE"
watcher = WatchDirectory(0)
watcher_xml = WatchDirectory(1)
waveformr = SimpleFunctionPE(waveform_reader)
xmlr = SimpleFunctionPE(stationxml_reader)
processes = [waveform_reader,
             (plot_stream, {"source": "waveform_reader", "output_dir": "./output-images", "tag": "observed-image"})]
chain = create_iterative_chain(processes, FunctionPE_class=SimpleFunctionPE)

graph = WorkflowGraph()
graph.connect(read_stream, "output", downloadPE, "input")
graph.connect(downloadPE, 'output', watcher, "input")
graph.connect(downloadPE, 'output', watcher_xml, "input")
graph.connect(watcher, 'output', chain, "input")
graph.connect(watcher_xml, 'output', xmlr, "input")
#write_image(graph, "downloadPE.png")


ProvenanceType.REPOS_URL=os.environ['REPOS_URL']
#rid='JUP_DOWNLOAD_'+getUniqueId()
rid=os.environ['DOWNL_RUNID']
prov_config =  {
                    'provone:User': "fmagnoni", 
                    's-prov:description' : "create and download data",
                    's-prov:workflowName': "create_download",
                    's-prov:workflowType': "seis:preprocess",
                    's-prov:workflowId'  : "workflow process",
                    's-prov:save-mode'   : 'service'         ,
                    's-prov:WFExecutionInputs':  [{
                        "url": "",
                        "mime-type": "text/json",
                        "name": "input_data"
                         
                     },{"url": "",
                     "prov:type": "wfrun",
                     "mime-type": "application/octet-stream",
                     "name": "create and download json"}
                     ],
    
                    # defines the Provenance Types and Provenance Clusters for the Workflow Components
                    's-prov:componentsType' : 
                                       {'PE_waveform_reader': {'s-prov:type':(SeismoPE,),
                                                     's-prov:prov-cluster':'seis:Reader'},
                                        
                                        },
                                        
                    's-prov:sel-rules': None
                } 
                


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
                



