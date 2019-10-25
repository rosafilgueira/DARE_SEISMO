import glob
import os
import numpy as np
import obspy


###################################################################################################################
###################################################################################################################
###################################################################################################################


'''

    Compare read function in write_CMTSOLutiON

'''

import zipfile
import requests

def CMTSOLUTION_syntax(content):
    list_output = {}
    for line in content:
        info = line.split(':')
        if len(info) == 1: # header line, no : included
            PDE = info[0].split()
            list_output['event time'] = obspy.UTCDateTime(int(PDE[1]),int(PDE[2]),int(PDE[3]),int(PDE[4]),int(PDE[5]),
                                                    float(PDE[6]))
            list_output['mb'] = float(PDE[10])
            list_output['Ms'] = float(PDE[11])
            list_output['event name'] = PDE[12]
        elif info[0] != 'event name':
            list_output[info[0]] = float(info[1])
    return list_output

def STATIONS_syntax(content):
    list_output = {}
    for line in content:
        info = line.split()
        list_output[info[0]] = [info[0],info[1],float(info[2]),float(info[3]),float(info[4])]
    return list_output

def create_dictionary(content):
    if content[0].startswith('PDE'): # case 1: input is CMTSOLUTION file
        list_output = CMTSOLUTION_syntax(content)
    else: # case 2: input is STATIONS file
        list_output = STATIONS_syntax(content)
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

###################################################################################################################
###################################################################################################################
###################################################################################################################




def create_mseed(r,rm,outputsuffix=None):
    
    """
    create mseed files from semv ascii files in directory r
    :type string r directory name
    """
    if outputsuffix is None: 
        outputsuffix='.synth' 
    else: 
        outputsuffix='.'+outputsuffix
    #get seismograms
    vname=glob.glob(os.path.join(r,'*.semv'))
    aname=glob.glob(os.path.join(r,'*.sema'))
    dname=glob.glob(os.path.join(r,'*.semd'))
    outputnames=['velocity','acceleration','displacement']
    #
    sts=[]
    for (oname,fname) in zip(outputnames,[vname,aname,dname]):
        print(oname,fname)
        traces=[]
        for filename in fname[:]:
            _splitname=filename.split('/')[-1].split('.')
            network=_splitname[0]
            station=_splitname[1]
            channel=_splitname[2]
            
            time,data=np.loadtxt(filename,unpack=True)
            dt = time[1]-time[0] # alternativ: np.diff of time vector --> np.mean(np.unique(np.diff(time)))
            tr = obspy.Trace(data=data)
            tr.stats.delta = dt
            '''
                starttime is set at 0 --> 1969
                this can later be changed during the saparation into sac files (see below)
                or should this be done here --> CMTSOLUTION file with starttime is in the same folder
                use: 
                    cmt = load_local_content(file_url='CMTSOLUTION')
                    tr.stats.starttime = cmt['event time']
            '''
            tr.stats.starttime = time[0] 
            tr.stats.network = network
            tr.stats.station = station
            tr.stats.channel = channel
            tr.stats.sampling_rate= 1./dt
            traces.append(tr)

        if len(traces) > 0:
            st=obspy.Stream(traces)
            st.write(os.path.join(rm,oname+outputsuffix+'.mseed'),format='MSEED')
    return outputsuffix+'.mseed'
            
            
            
def convert_mseed_to_sac(file_type,path2mseed,path2sac,zip_file_url):
    """convert mseed in sac (one sac files for each components)
    
    ms: name of mseed file 
    zip_file_url: path to data.zip with content CMTSOLUTION, STATIONS, PAR_FILE
    
    it assumes to run in [DIR iteration]/
    
    """
    
    # get data_type and suffix     
    print(path2mseed)
    if file_type == 'synthetics': 
        data_type = path2mseed.split('.')[-3] # sema,semv,semd
        suffix = path2mseed.split('.')[-2] # Mrr,...
    
    #create new folder
    if not os.path.exists(path2sac):    os.mkdir(os.path.join(path2sac,rid+'_mseed'))
    
    # get location and time information from CMTSLUTION and STATIONS file within data.zip
    stationfile = download_file_content(file_url=zip_file_url,fname='STATIONS')
    cmt = download_file_content(file_url=zip_file_url,fname='CMTSOLUTION')
    late, lone = cmt['latorUTM'],cmt['latorUTM']


    stream=obspy.read(path2mseed)
    for v in stream[:]:
        # create SAC header object
        v.stats.sac = obspy.core.AttribDict()
        v.stats.sac.stla = stationfile[v.stats.station][2]
        v.stats.sac.stlo = stationfile[v.stats.station][3]
        
        # ISSUE: Why? TODO: add starttime information from cmt file (in sac or obspy header?)
        # SAC time: b:begin, e:end (http://geophysics.eas.gatech.edu/classes/SAC/)
        v.stats.sac.b = v.stats.starttime-obspy.UTCDateTime(0)
        v.stats.sac.e = v.stats.sac.b+(v.stats.npts-1)*v.stats.delta
        
        # Source-Receiver location information
        v.stats['coordinates']={'latitude':v.stats.sac.stla,'longitude':v.stats.sac.stlo}
        v.stats['distance'] = obspy.geodetics.base.gps2dist_azimuth(v.stats.sac.stla, v.stats.sac.stlo, late, lone)[0]
        v.stats.sac.evla = late
        v.stats.sac.evlo = lone
        v.stats.sac.dist,v.stats.sac.az,v.stats.sac.baz=obspy.geodetics.base.gps2dist_azimuth(v.stats.sac.stla, v.stats.sac.stlo,v.stats.sac.evla, v.stats.sac.evlo)
        
        # save split traces
        if file_type == 'observed': name=os.path.join(path2sac,+'.s.sac')       
        if file_type == 'synthetics': 
            if suffix == 'synth':
                name=os.path.join(path2sac,v.id)
            else:
                name=os.path.join(path2sac,v.id+'.'+suffix)
        v.write(name,format='SAC')
        
    # Needed?
    #stream.write(ms,format='MSEED')


r = 'OUTPUT_FILES/'
rm = 'MSEED/'
rs = 'SAC/'
zip_file_url = 'data.zip'
file_type = 'synthetics'
Suffix = [None,"Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp","dep","lat","lon"]
for outputsuffix in Suffix:
    filename = create_mseed(r,rm,outputsuffix=outputsuffix)
    path2mseed = rm+'velocity'+filename # set data_type (velocity, etc.) based on the folder naming (?) of the mseed files
    convert_mseed_to_sac(file_type,path2mseed,rs,zip_file_url)



