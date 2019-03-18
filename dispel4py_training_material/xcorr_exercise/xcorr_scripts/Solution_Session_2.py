from obspy.core import read

sta1 = 'http://escience8.inf.ed.ac.uk:8080/laquila/SAC/A25A.TA..BHZ.2011.025.00.00.00.000-2011.026.00.00.39.000.rm.scale-AUTO.SAC'
sta2 = 'http://escience8.inf.ed.ac.uk:8080/laquila/SAC/BMN.LB..BHZ.2011.025.00.00.00.023-2011.026.00.00.38.998.rm.scale-AUTO.SAC'


# The first two functions are similar to the ones in the previous sessions. The first one (stream_producer) reads a file that contains seismological traces and returns it as an obspy stream. The second one (readstats) extracts the start time and the station name of the first trace and returns a stream with those three values: starttime, station name and the obspy stream containing the trace. The reason for returning those values is that later we are going to group the data by start time and station for computing the cross correlation.

from dispel4py.base import SimpleFunctionPE, IterativePE, create_iterative_chain
def stream_producer(data):
    filename = data
    st = read(filename)
    return st

def readstats(st):
    station_date = st[0].stats['starttime'].date
    station_day = station_date.strftime('%d-%m-%Y')
    station = st[0].stats['station']
    return [station_day, station, st]


# This is the 'preprocess pipeline' which is a composite PE for processing several functions (decimate, detrend and demean) in a sequence.

def decimate(st, sps):
    st.decimate(int(st[0].stats.sampling_rate/sps))
    return st

def detrend(st):
    st.detrend('simple')
    return st

def demean(st):
    st.detrend('demean')
    return st

def filter(st, freqmin=0.01, freqmax=1., corners=4, zerophase=False):
    st.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=corners, zerophase=zerophase)
    return st


# Now, we create another function for whitening obspy stream.

from numpy import arange, sqrt, abs, multiply, conjugate, real
from obspy.signal.util import next_pow_2
from scipy.fftpack import fft, ifft

def spectralwhitening(st):
    """
    Apply spectral whitening to data.
    Data is divided by its smoothed (Default: None) amplitude spectrum.
    """
    
    for trace in arange(len(st)):
        data = st[trace].data
        
        n = len(data)
        nfft = next_pow_2(n)
        
        spec = fft(data, nfft)
        spec_ampl = sqrt(abs(multiply(spec, conjugate(spec))))
        
        spec /= spec_ampl  #Do we need to do some smoothing here?
        ret = real(ifft(spec, nfft)[:n])
        
        st[trace].data = ret
        
    return st


# Now it's time to create the graph for preprocessing the traces.


from dispel4py.workflow_graph import WorkflowGraph
streamProducer = SimpleFunctionPE(stream_producer)
streamProducer.name = "streamProducer"
sta = SimpleFunctionPE(readstats) 

preprocess_trace = create_iterative_chain([
    (decimate, {'sps':4}), 
    detrend, 
    demean, 
    (filter, {'freqmin':0.01, 'freqmax':1., 'corners':4, 'zerophase':False}),
    spectralwhitening])

graph = WorkflowGraph()
graph.connect(streamProducer, 'output', preprocess_trace, 'input')
graph.connect(preprocess_trace, 'output', sta, 'input')


# Now execute the graph:
# Simple command for executing this workflow from a terminal. 


# dispel4py simple Solution_Session_2.py -d '{ "streamProducer" : [ {"input": "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/A25A.TA..BHZ.2011.025.00.00.00.000-2011.026.00.00.39.000.rm.scale-AUTO.SAC"}, {"input": "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/BMN.LB..BHZ.2011.025.00.00.00.023-2011.026.00.00.38.998.rm.scale-AUTO.SAC"} ] }'
