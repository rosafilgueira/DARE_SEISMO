from obspy.core import read

from dispel4py.base import SimpleFunctionPE, IterativePE


def stream_producer(data):
    '''
    This function reads a file that contains seismological traces
    and returns it as an obspy stream.

    For using this function as a PE we need to do before defining the graph:
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

#  As follows we are going to create two PEs whose aims are the same as
# 'stream_producer' function. This means that both PEs read a file with
# seismological traces and return an stream. However, the
# 'StreamAndStatsProducer' PE not only returns an obspy stream,
# it also returns the metadata.


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
        # This PE returns two outputs:
        # the output stream and the trace statistics (metadata).
        return {'output': st, 'output_stats': st[0].stats}


# This fuctions prints the name of an station from the stats.

def name_station(stats):
    station_name = stats['station']
    print('Station: ' + station_name)
    return stats


from dispel4py.workflow_graph import WorkflowGraph

nameStation = SimpleFunctionPE(name_station)
streamProducer = StreamAndStatsProducer()
streamProducer.name = "streamProducer"
readStats = ReadStats()
graph = WorkflowGraph()
graph.connect(streamProducer, 'output', readStats, 'input')
# The following line can be only performed if streamProducer is
# a StreamAndStatsProducer object
graph.connect(streamProducer, 'output_stats', nameStation, 'input')


def detrend(st):
    st.detrend('simple')
    return st

detrendPE = SimpleFunctionPE(detrend)
graph.connect(readStats, 'output', detrendPE, 'input')


def read_samplingrate(data):
    st = data
    srate = st[0].stats['sampling_rate']
    return srate


samplingratePE = SimpleFunctionPE(read_samplingrate)
samplingratePE.name = 'SamplingRate'
graph.connect(detrendPE, 'output', samplingratePE, 'input')


# Now execute the graph:
# Simple command for executing this workflow from a terminal.


# dispel4py simple Solution_Session_1.py -d '{ "streamProducer" : [ { "input" : "../20100501.fseed" } ] }'
