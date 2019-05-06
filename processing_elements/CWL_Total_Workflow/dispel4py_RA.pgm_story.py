'''
Execution:
Real --> dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducer": [ {"input": "IV.MA9..HHR.START.OTLOC.SAC.20.50.real"} ] }'
Synth --> dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducer": [ {"input": "IV.MA9.HXR.semv.sac.20.50.synt"} ] }'


Comparison:
dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input": "IV.MA9..HHR.START.OTLOC.SAC.20.50.real"} ], "streamProducerSynth": [ {"input": "IV.MA9.HXR.semv.sac.20.50.synt"} ]   }'

Output:
WriteStream3: output_data is {'GroundMotion': {'stream': 'IV.MA9..HHR.START.OTLOC.SAC.20.50.real', 'ty': 'velocity', 'p_norm': 'max', 'pgd': '0.0006945877', 'pgv': '0.0002320527', 'pga': '0.00013708159', 'dmp_spec_acc': '0.00032428280150622804'}}

'''

from dispel4py.core import GenericPE
from dispel4py.base import BasePE, IterativePE, ConsumerPE, create_iterative_chain
from dispel4py.workflow_graph import WorkflowGraph

from obspy.core.stream import read
from obspy.signal.invsim import corn_freq_2_paz, simulate_seismometer
from obspy.signal import differentiate_and_integrate as di

import math
import numpy as np
import os
import json
from collections import defaultdict

def calculate_norm(stream):
    station = stream[0].stats.station
    channels = set()
    for tr in stream:
        if station == tr.stats.station:
            channels.add(tr.stats.channel[-1])
        else:
            return None

    data_mean = None
    data_max = None
    if channels < set(['R','T']) or channels < set(['N','E']):

        if len(stream) == 1:
            return stream[0].data.copy(), stream[0].data.copy(), None

        for tr in stream:
            d = tr.data.copy()
            if data_mean is None:
                data_mean = np.square(d)
                data_max = np.abs(d)
            else:
                data_mean = data + np.square(d)
                data_max = data + np.abs(d)

        data_mean = np.sqrt(data)
        data_max = np.max(data)

    return data_mean, data_max, d

def calculate_pgm(data, ty, delta):
    pgm = max(abs(data))
    if ty == 'velocity':
        pgv = pgm
        int_data = di.integrate_cumtrapz(data, delta)
        pgd = max(abs(int_data))
        grad_data = np.gradient(data, delta)
        pga = max(abs(grad_data))
    elif ty == 'displacement':
        pgd = pgm
        grad_data = np.gradient(data, delta)
        pgv = max(abs(grad_data))
        grad2_data = np.gradient(grad_data, delta)
        pga = max(abs(grad2_data))
    elif ty == 'acceleration':
        pga = pgm
        int_data = di.integrate_cumtrapz(data, delta)
        pgv = max(abs(int_data))
        int2_data = di.integrate_cumtrapz(int_data, delta)
        pgd = max(abs(int2_data))
    return pgd, pgv, pga

def calculate_damped_spectral_acc(data,delta,freq,damp,ty):

    samp_rate = 1.0 / delta
    t = freq * 1.0
    d = damp
    omega = (2 * math.pi * t) ** 2

    paz_sa = corn_freq_2_paz(t, damp=d)
    paz_sa['sensitivity'] = omega
    paz_sa['zeros'] = []

    if ty == 'displacement':
        data = np.gradient(data, delta)
        data = np.gradient(data, delta)
    elif ty == 'velocity':
        data = np.gradient(data, delta)

    data = simulate_seismometer(data, samp_rate, paz_remove=None,
                            paz_simulate=paz_sa, taper=True,
                            simulate_sensitivity=True, taper_fraction=0.05)
    dmp_spec_acc = max(abs(data))

    return dmp_spec_acc


class StreamProducer(IterativePE):

    def __init__(self, label):
        IterativePE.__init__(self)
        self.label = label

    def _process(self, input):
        filename =  input
        self.write('output', [read(filename), self.label])


class NormPE(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input("input")
        self._add_output("output_mean")
        self._add_output("output_max")

    def _process(self, data):
        stream, filename = data['input']
        data_mean, data_max, d = calculate_norm(stream)
        self.write('output_mean', [stream, filename, data_mean, 'mean'])
        self.write('output_max', [stream, filename, data_max, 'max'])


class PeakGroundMotion(IterativePE):
    def __init__(self,ty,freq=(0.3, 1.0, 3.0),damp=0.1):
        IterativePE.__init__(self)
        self.ty=ty
        self.frequencies = freq
        self.damp = damp

    def _process(self, s_data):
        stream, filename, data, p_norm = s_data
        delta = stream[0].stats.delta
        pgd, pgv, pga = calculate_pgm(data, self.ty, delta)
        dmp_spec_acc = {}
        for freq in self.frequencies:
            dmp = calculate_damped_spectral_acc(data, delta, freq, self.damp, self.ty)
            dmp_spec_acc['PSA_{}Hz'.format(freq)] = dmp.item()

        results = {
            'PGD': pgd.item(),
            'PGV': pgv.item(),
            'PGA': pga.item(),
            'p_norm': p_norm
        }
        results.update(dmp_spec_acc)
        self.write('output', [
            stream[0].stats.station,
            filename, stream, self.ty, results]
        )


class Match(GenericPE):
    def __init__(self):
        GenericPE.__init__(self)
        self._add_input('input', grouping=[0])
        self._add_output('output')
        self.store = defaultdict(lambda: {})

    def _process(self, data):
        station, label,stream, ty, pgm = data['input']
        p_norm = pgm['p_norm']
        self.store[(station, p_norm)][label] = stream, ty, pgm
        if len(self.store[(station, p_norm)]) >= 2:
            print('output: {} {}'.format(station, p_norm))
            self.write('output', [station, p_norm, self.store[(station, p_norm)]])
            del self.store[station, p_norm]


def comp(real_param, synt_param):
    result_diff = real_param - synt_param
    result_rel_diff = (real_param - synt_param)/real_param
    return result_diff, result_rel_diff


class WriteGeoJSON(ConsumerPE):
    def __init__(self):
        ConsumerPE.__init__(self)

    def _process(self, data):
        station, p_norm, matching_data = data

        difference = { }
        relative_difference = {}
        stream_r, ty_r, pgm_r = matching_data['real']
        stream_s, ty_s, pgm_s = matching_data['synth']
        try:
            sac = stream_r[0].stats.sac
            coordinates = [sac.stla.item(), sac.stlo.item()]
        except:
            coordinates = []
        for param in pgm_r:
            if param == 'p_norm':
                continue
            diff, rel_diff = comp(pgm_r[param], pgm_s[param])
            difference[param] = diff
            relative_difference[param] = rel_diff

        output_dir = os.environ['OUTPUT'] 
        if not os.path.exists(output_dir):
           try:
              os.makedirs(output_dir)
           except:
              pass
        output_data={
            "type": "Feature",
            "properties": {
                "station": station,
                "data": pgm_r,
                "synt": pgm_s,
                "difference": difference,
                "relative_difference": relative_difference,
                "geometry": {
                  "type": "Point",
                  "coordinates": coordinates
                }
            }
        }
        # self.log("output_data is %s" % json.dumps(output_data))
        filename = "./{}_{}.json".format(station, p_norm)
        with open(output_dir+filename, 'w') as outfile:
            json.dump(output_data, outfile)


streamProducerReal=StreamProducer('real')
streamProducerReal.name="streamProducerReal"
streamProducerSynth=StreamProducer('synth')
streamProducerSynth.name='streamProducerSynth'
norm=NormPE()
pgm_mean=PeakGroundMotion('velocity')
pgm_max=PeakGroundMotion('velocity')
match = Match()
write_stream = WriteGeoJSON()


graph = WorkflowGraph()
graph.connect(streamProducerReal, 'output', norm,'input')
graph.connect(streamProducerSynth, 'output', norm,'input')
graph.connect(norm, 'output_mean', pgm_mean,'input')
graph.connect(norm, 'output_max', pgm_max,'input')
graph.connect(pgm_max, 'output', match, 'input')
graph.connect(pgm_mean, 'output', match, 'input')
graph.connect(match,'output',write_stream,'input')

