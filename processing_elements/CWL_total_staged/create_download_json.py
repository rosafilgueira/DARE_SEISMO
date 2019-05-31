from dispel4py.base import SimpleFunctionPE
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.base import create_iterative_chain, ConsumerPE, IterativePE

import obspy
from obspy.core import read

import zipfile
import requests,json
import io
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO



import sys,os
import re
import numpy


def get_file_content(file_url=None,directory=None,
                     fname='Par_file',
                     json_format=False,zip_format=False):
    if zip_format:
        try:
            try:
                response = requests.get(file_url)
                zfiles=zipfile.ZipFile(io.BytesIO(response.content))
            except:
                zfiles=zipfile.ZipFile(file_url)
            listfile = zfiles.namelist()
        except:
             print('ERROR: Error reading zip file %s' % file_url)
        
        try:
            parfound=False
            for f in listfile:
                if fname in f:
                    ifile = zfiles.read(f)
                    parfound=True
                    break
        except KeyError:
            parfound=False
        
        if not parfound: 
            print('ERROR: Did not find %s in zip file' % fname)
            return None

    elif directory:
        try:
            f.open(os.path.join(directory,fname),'r')
            ifile=f.read()
        except:
            print('ERROR: Error reading %s file in %s' % (fname,directory))
    elif json_format:
        try:
            try:
                response = requests.get(file_url)
                ifile=response.json()
            except:
                ifile=json.loads(file_url)
        except:
             print('ERROR: Error reading json file %s' % file_url)
    return ifile

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
        print('no parameter found')
        return None

def create_event_time(event_time):
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



class WriteJSON(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self)

    def _process(self, data):
        
        data_url='https://gitlab.com/project-dare/dare-api/raw/master/containers/specfem3d/data.zip' 
        cmtsolution=get_file_content(file_url=data_url,fname='CMTSOLUTION',zip_format=True)
        parfile=get_file_content(file_url=data_url,zip_format=True)
        
        infopar=get_file_content(file_url='https://gitlab.com/project-dare/WP6_EPOS/raw/master/specfem3d/specfem3d_input/DATA/mesh_Abruzzo/Info.json',
                        directory=None,json_format=True)
        meshfile=get_file_content(file_url=data_url,directory=None,fname='nodes_coords',zip_format=True)
        
        
        NPROC=int(get_parameter('NPROC',parfile))
        dt=float(get_parameter('DT',parfile))
        nstep=int(get_parameter('NSTEP',parfile))
        try:
            RECORD_LENGTH_IN_MINUTES=float(get_parameter('RECORD_LENGTH_IN_MINUTES',parfile))
        except:
            RECORD_LENGTH_IN_MINUTES=dt*nstep/60.
        
        ETIME=create_event_time(event_time)
        
        lim=get_coordlimits(meshfile)
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
                        "maxlongitude": longitude_min
                        }
                    }
                ]
        }
        output_dir = os.environ['OUTPUT']
        filename = "{}/data_file.json".format(output_dir)
        with open(filename, "w") as write_file:
            json.dump(d, write_file)



write_stream = WriteJSON()

graph = WorkflowGraph()

