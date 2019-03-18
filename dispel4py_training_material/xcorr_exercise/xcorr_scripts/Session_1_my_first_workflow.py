from obspy.core import read

from dispel4py.base import SimpleFunctionPE, IterativePE, create_iterative_chain

def stream_producer(data):
    '''
    This function reads a file that contains seismological traces 
    and returns it as an obspy stream.
    
    For using this function as a PE we need to use 'SimpleFunctionPE' before 
    defining the graph:
    streamProducer = SimpleFunctionPE(stream_producer)
    '''
    filename = data
    st = read(filename)
    return st

class ReadStats(IterativePE):
    '''
    This PE reads the stats of the first trace and prints it out to the log.
    '''
    def __init__(self):
        IterativePE.__init__(self)
    def _process(self, data):
        st = data
        # print out the stats of the stream
        self.log(st[0].stats)
        return st
    

class StreamProducer(IterativePE):
    '''
    This PE also reads a file that contains seismological traces 
    and returns it as an obspy stream. 
    
    It is similar to the function 'stream_producer'.
    We could use this PE directly, without calling SimpleFunctionPE. 
    '''
    def __init__(self):
        IterativePE.__init__(self)
    def _process(self, data):
        # this PE consumes one input
        self.log(data)
        filename = data
        st = read(filename)
        return st


from dispel4py.core import GenericPE


class StreamAndStatsProducer(GenericPE):
    '''
    This PE also reads a file that contains seismological traces 
    and returns two outputs: obspy stream and metadata. 
    
    It is similar to the function 'stream_producer' and 'StreamProducer' PE.
    We could use this PE directly, without calling SimpleFunctionPE. 
    '''
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input')
        self._add_output('output')
        self._add_output('output_stats')
    def process(self, inputs):
        data = inputs['input']
        # this PE consumes data in the format [url] - a list with one element
        filename = data
        st = read(filename)
        # This PE returns two outputs: the output stream and the trace stadistics (metadata).
        return {'output': st, 'output_stats': st[0].stats}


def name_station(stats):
    station_name = stats['station']
    print 'Station: ' + station_name
    return stats


# Create a graph which connects the streamProducer to the ReadStats PE and to a SimpleFunctionPE with function name_station.

from dispel4py.workflow_graph import WorkflowGraph
'''
Using the stream_producer function:
'''
nameStation = SimpleFunctionPE(name_station)
streamProducer = StreamAndStatsProducer()
streamProducer.name="streamProducer"
'''
streamProducer = SimpleFunctionPE(stream_producer)
streamProducer = StreamProducer()
'''
readStats = ReadStats()


graph = WorkflowGraph()
#graph.connect( ... )




# Connect the ReadStats PE to the detrend PE. Note: You have to use SimpleFunctionPE for converting 'detrend' function to a PE

# In[ ]:

def detrend(st):
    st.detrend('simple')
    return st


# Now execute the graph:

# dispel4py simple Session_1_my_first_workflow.py -d '{ "streamProducer" : [ { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/20100501-20120930_fseed/TERO/20100101.fseed" } ]' 



# Create a PE (recommended: a function and a SimpleFunctionPE) called 'samplingratePE' that reads the sampling rate from the stream stats and connect it to the graph.

def read_samplingrate(data):
    '''
    Write your code here.
    '''  

    
samplingratePE = SimpleFunctionPE(read_samplingrate)
samplingratePE.name = 'SamplingRate'

'''
Connect the 'samplingratePE' to the 'preprocess_trace' composite PE
'''  


# Now execute the graph:

# dispel4py simple Session_1_my_first_workflow.py -d '{ "streamProducer" : [ { "input" : "http://escience8.inf.ed.ac.uk:8080/laquila/20100501-20120930_fseed/TERO/20100101.fseed" } ]' 
