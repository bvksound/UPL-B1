import time

import matplotlib.pyplot as plt
import numpy as np
import pyvisa
import scipy.signal

from instruments.rigol import RigolScope
from upl_control import Testjig

# Debugging/Diagnostic tool for UPL-B1-Cards
#
# Use with a rigol scope (e.g. DS1054) connected via USB
#
# The scopes channes are to be connected to the the B1 as follows:
B1_MAPPING = {1: "P32", 2: "P40", 3: "P53", 4: "P58"}

rm = pyvisa.ResourceManager()

rigol = RigolScope(rm)
jig = Testjig("/dev/ttyACM0")


def lowpass(data: np.ndarray, cutoff: float, sample_rate: float, poles: int = 5):
    sos = scipy.signal.butter(poles, cutoff, "lowpass", fs=sample_rate, output="sos")
    filtered_data = scipy.signal.sosfiltfilt(sos, data)
    return filtered_data


def measure_settling_time(freq_range, coarse, gain, tune):
    # Set up measurement
    rigol.set_trigger(3, level=1, slope="POSITIVE", mode="NORMAL")
    rigol.channel(1, display=False)
    rigol.channel(2, display=False)
    rigol.channel(3, display=True, coupling="DC", scale=1, offset=1)
    rigol.channel(4, display=True, coupling="DC", scale=1, offset=-1)
    rigol.timebase(1e-3, left=True)
    time.sleep(1)
    rigol.clear()
    jig.vars["freq_range"] = freq_range
    jig.vars["gain"] = gain
    jig.vars["freq_coarse"] = coarse
    jig.vars["tune"] = tune
    jig.set_state()
    # Now we get a waveform reading
    yinc, wave = rigol.read_waveform()

    # We need to determine the output signal frequency, too
    rigol.channel(2, display=True, coupling="DC", scale=1)
    out_freq = rigol.measure_freq(2)

    settling = lowpass(wave, out_freq / 2, 1 / yinc)
    # Find maximum of the signal
    peak = max(settling)
    peak_pos = np.argmax(settling)
    # Find time signal has stopped oscillation
    # Now lowpass-filter the signal in order to only see the settling


def measure_frequency_response():
    # Set up scope, first
    rigol.set_trigger(2, 0, slope="POSITIVE", mode="NORMAL")
    rigol.channel(1, "DC", display=True, scale=1, offset=0)
    rigol.channel(2, "DC", display=True, scale=1, offset=0)
    rigol.channel(3, "DC", display=True, scale=0.5, offset=0)
    rigol.channel(4, "DC", display=True, scale=0.5, offset=0)

    freq = 0
    for freq_range in [0, 1, 2, 4]:
        jig.vars["freq_range"] = freq_range
        for coarse in range(16):
            jig.vars["freq_coarse"] = coarse
            for gain in range(100, 0x1000, 0x1FF):
                jig.vars["gain_adj"] = gain
                jig.vars["imd_gain"] = gain
                for tune in range(100, 0x1000, 0x1FF):
                    jig.vars["freq_tune"] = tune
                    jig.set_state()
                    time.sleep(0.1)
                    # Measure an average of five samples

                    # Let the hardware settle for a bit (100 waves at least)
                    trigger = 1
                    scale = 2
                    while not (1 < freq < 1e6):
                        print(trigger, flush=True)
                        rigol.set_trigger(trigger, mode="NORMAL")
                        rigol.channel(1, scale=scale, offset=0)
                        rigol.channel(2, scale=scale, offset=0)
                        time.sleep(1)
                        freq = rigol.measure_freq(1)
                        if trigger == 1:
                            trigger = 2
                        else:
                            trigger = 1
                            scale /= 2
                            if scale < 0.5:
                                scale = 0.2

                    time.sleep(100 / freq)

                    rms = {}
                    avg = {}
                    freq = 9e99

                    for scale in [2, 1, 0.5, 0.2]:
                        rigol.channel(1, scale=scale, offset=0)
                        rigol.channel(2, scale=scale, offset=0)
                        time.sleep(1)
                        for channel in [1, 2, 3, 4]:
                            if channel not in rms or rms[channel] > 1e32:
                                rms[channel] = rigol.measure_rms(channel)
                            if channel not in avg or avg[channel] > 1e32:
                                avg[channel] = rigol.measure_avg(channel)
                        if freq > 1e35:
                            freq = rigol.measure_freq(1)
                        if max(max(max(rms.values()), max(avg.values())), freq) < 1e35:
                            break
                    print(
                        freq_range,
                        coarse,
                        gain,
                        tune,
                        freq,
                        *rms.values(),
                        *avg.values(),
                        flush=True,
                    )


# Set some known state on the B1 so we get (some) output
jig.set_state()

measure_frequency_response()
