# In this exercise, we're going to build a small preprocessing workflow that prepares traces and then computes the cross correlation from the results.

from obspy.core import read
sta1 = 'http://escience8.inf.ed.ac.uk:8080/laquila/SAC/A25A.TA..BHZ.2011.025.00.00.00.000-2011.026.00.00.39.000.rm.scale-AUTO.SAC'
sta2 = 'http://escience8.inf.ed.ac.uk:8080/laquila/SAC/BMN.LB..BHZ.2011.025.00.00.00.023-2011.026.00.00.38.998.rm.scale-AUTO.SAC'


# The first two functions are similar than the ones in the previous sesions. The first one (stream_producer) reads a file that contains seismological traces and returns it as an obspy stream. The second one (redstats) extracts the station's start time, the station's name of the first trace and returns a stream with three values: station's starttime, station's name and the obspy stream. The reason for returning those values, is because later we are going to group the data by station's start time for computing the cross correlation.


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


# Functions to preprocess data

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


# This is the 'preprocess pipeline' which is a composite PE for processing several functions (decimate, detren and deman) in a sequence.

# You can create a pipeline of processing elements that run a list of functions, for example, this creates a chain with the functions decimate and detrend. Note that decimate has one parameter 'sps' with value 4.

preprocess_trace = create_iterative_chain([detrend ])


# This creates a composite PE which you can also visualise as a graph.

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


# Create your own function to preprocess the data. It later could be added to the CompositePE. 

# Now it's time to create the graph for preprocessing the traces. 
# 
# An example of the filter parameter that can be used is :
# 'freqmin':0.01, 'freqmax':1., 'corners':4, 'zerophase':False. 
# 
# Remenber that the worfklow first has to read the file that contains the traces, then preprocess them (composite PE), and finally extract the station's start time,  the station's name and stream. You can chose how many functions want to add to the create_iterative_chain for preprocess the traces.  

from dispel4py.workflow_graph import WorkflowGraph
streamProducer = SimpleFunctionPE(stream_producer) 
streamProducer.name="streamProducer"
preprocess_trace = create_iterative_chain([ (decimate, {'sps':4}), detrend, demean, spectralwhitening ])
readStats=SimpleFunctionPE(readstats)

graph = WorkflowGraph()
graph.connect(streamProducer, 'output', preprocess_trace,'input')
graph.connect(preprocess_trace, 'output', readstats,'input')



# Finally execute the graph and preprocess the traces from two different stations. 
# dispel4py simple Session_2_xcorr.py -d '{ "StreamProducer" : [ { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/A25A.TA..BHZ.2011.025.00.00.00.000-2011.026.00.00.39.000.rm.scale-AUTO.SAC" }, { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/BMN.LB..BHZ.2011.025.00.00.00.023-2011.026.00.00.38.998.rm.scale-AUTO.SAC"} ] }'

# MPI mapping for a distributed memory machine (several cores in several cpus):
# 
# mpiexec -n 4 dispel4py mpi Session_2_xcorr -d '{ "StreamProducer" : [ { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/A25A.TA..BHZ.2011.025.00.00.00.000-2011.026.00.00.39.000.rm.scale-AUTO.SAC" }, { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/SAC/BMN.LB..BHZ.2011.025.00.00.00.023-2011.026.00.00.38.998.rm.scale-AUTO.SAC"} ] }'



# Convert 'decimate' function into a IterativePE called DecimatePE. </p>
# Modify the graph for using the DecimatePE:
# 
#  - modify the compositePE (preprocess_trace) to remove decimate function from the creative_iterative_chain
#  - create the decimatePE object
#  - connect streamProducer to decimantePE
#  - connect decimatePE to preprocess_trace

class DecimatePE(IterativePE):

    def __init__(self):
        IterativePE.__init__(self)

    def _process(self, data):
        st=data
        st.decimate(int(st[0].stats.sampling_rate/self.sps))
        return st

decimate =  DecimatePE(4)
preprocess_trace = create_iterative_chain([
    (decimate, {'sps':4}), 
    detrend, 
    demean, 
    spectralwhitening])

streamProducer=

graph = WorkflowGraph()
graph.connect(streamProducer, 'output', decimate, 'input')
graph.connect(decimate, 'output', preprocess_trace, 'input')
