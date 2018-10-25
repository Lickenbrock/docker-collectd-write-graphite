#!/usr/bin/env python

import collectd
import subprocess
import xml.etree.ElementTree as ET


def configure_callback(conf):
    collectd.info('Configured with')


def read(data=None):
    vl = collectd.Values(type='gauge')
    vl.plugin = 'cuda'

    out = subprocess.Popen(['nvidia-smi', '-q', '-x'],
                           stdout=subprocess.PIPE).communicate()[0]
    root = ET.fromstring(out)

    # Changed root.iter() to root.getiterator() for Python 2.6 compatibility

    for gpu in root.iter('gpu'):
        # GPU id
        vl.plugin_instance = 'gpu-%s' % (gpu.find('minor_number').text)

        # GPU utilization
        vl.dispatch(type='percent', type_instance='gpu_util',
                    values=[float(
                            gpu.find('utilization/gpu_util').text.split()[0])])
        # GPU temperature
        vl.dispatch(type='temperature',
                    values=[float(
                           gpu.find('temperature/gpu_temp').text.split()[0])])
        # GPU power draw
        #    vl.dispatch(type='power', type_instance='power_draw',
        #                values=[float(gpu.find('power_readings/power_draw').text.split()[0])])
        # GPU memory utilization
        vl.dispatch(type='percent', type_instance='mem_util',
                    values=[float(
                            gpu.find(
                                    'utilization/memory_util'
                                    ).text.split()[0])])
        # GPU encoder utilization
        vl.dispatch(type='percent', type_instance='enc_util',
                    values=[float(
                           gpu.find(
                                    'utilization/encoder_util'
                                    ).text.split()[0])])
        # GPU memory usage
        vl.dispatch(type='memory', type_instance='used',
                    values=[1e6 * float(
                            gpu.find('fb_memory_usage/used').text.split()[0])])
        # GPU total memory
        vl.dispatch(type='memory', type_instance='total',
                    values=[1e6 * float(
                        gpu.find('fb_memory_usage/total').text.split()[0])])


collectd.register_config(configure_callback)
collectd.register_read(read)
