import time

import numpy as np
import pandas as pd
import pyvisa
import scipy.signal
import universal_usbtmc.exceptions

from instruments.rigol import RigolScope
from UPL import UPL
from upl_control import Testjig

# Debugging/Diagnostic tool for UPL-B1-Cards
#
# Use with a rigol scope (e.g. DS1054) connected via USB
#
# The scopes channes are to be connected to the the B1 as follows:
B1_MAPPING = {1: "P32", 2: "P40", 3: "P53", 4: "P58"}

rm = pyvisa.ResourceManager()

rigol = RigolScope(rm)
upl = UPL(addr=20)
jig = Testjig("/dev/ttyACM0")


def lowpass(data: np.ndarray, cutoff: float, sample_rate: float, poles: int = 5):
    sos = scipy.signal.butter(poles, cutoff, "lowpass", fs=sample_rate, output="sos")
    filtered_data = scipy.signal.sosfiltfilt(sos, data)
    return filtered_data


def measure_settling_time(from_range, to_range, coarse, gain, tune):
    # Set up measurement
    if to_range == 0:
        rigol.timebase(200e-6, left=True)
    if to_range == 1:
        rigol.timebase(10e-3, left=True)
    if to_range == 2:
        rigol.timebase(100e-3, left=True)
    if to_range == 4:
        rigol.timebase(500e-3, left=True)
    rigol.set_trigger(3, level=0.5, slope="NEGATIVE", mode="NORMAL")
    rigol.channel(1, display=False)
    rigol.channel(2, display=False)
    rigol.channel(3, display=True, coupling="DC", scale=1, offset=1)
    rigol.channel(4, display=True, coupling="DC", scale=1, offset=-1)
    rigol.stop()
    jig.vars["freq_range"] = from_range
    jig.vars["gain"] = gain
    jig.vars["freq_coarse"] = coarse
    jig.vars["tune"] = tune
    jig.set_state()
    time.sleep(2)
    jig.vars["gain"] = gain
    rigol.clean()
    rigol.run()
    time.sleep(1)
    jig.set_state()
    time.sleep(10)
    # Now we get a waveform reading
    print("reading wave")
    yinc, wave3 = rigol.read_waveform(3)
    _, wave4 = rigol.read_waveform(4)
    print("done")
    return (wave3, wave4, yinc)
    # settling = lowpass(wave, out_freq / 2, 1 / yinc)
    # Find maximum of the signal
    # peak = max(settling)
    # peak_pos = np.argmax(settling)
    # Find time signal has stopped oscillation
    # Now lowpass-filter the signal in order to only see the settling


def run_settling_times():
    data = {}
    for f in [0, 1, 2, 4]:
        for t in [0, 1, 2, 4]:
            try:
                data[(f, t)] = measure_settling_time(f, t, 5, 0x200, 0x200)
                with open(f"settle_{f}_{t}.png", "wb") as out:
                    out.write(rigol.take_screenshot())
                print(f, t, len(data))
            except universal_usbtmc.exceptions.UsbtmcReadTimeoutError:
                print("fail", f, t)
                continue
    df = pd.DataFrame()
    for r in data:
        ystep = data[r][2]
        a = pd.DataFrame(data[r][0])
        b = pd.DataFrame(data[r][1])
        a[2] = b
        timestamp = np.arange(0, len(data[r][0])) * ystep
        a["time"] = timestamp
        a.set_index(timestamp)
        a.to_csv(f"settle_{r}.csv")


def measure_frequency_response():
    freq = 0
    for freq_range in [0, 1, 2, 4]:
        jig.vars["freq_range"] = freq_range
        for coarse in range(16):
            jig.vars["freq_coarse"] = coarse
            for gain in range(100, 0xF00, 0x1FF):
                jig.vars["gain_adj"] = gain
                jig.vars["imd_gain"] = gain
                for tune in range(100, 0xF00, 0x1FF):
                    jig.vars["freq_tune"] = tune
                    jig.set_state()
                    time.sleep(0.1)
                    # Measure an average of five samples

                    # Let the hardware settle for a bit (100 waves at least)
                    trigger = 1
                    scale = 2
                    freq = 1e33

                    time.sleep(100 / freq)

                    upl.single_shot()

                    upl.wait_settle()

                    thdn = upl.data[0][0].get()
                    rms = upl.data[1][0].get()
                    freq = upl.data[2][0].get()

                    print(
                        freq_range,
                        coarse,
                        gain,
                        tune,
                        freq,
                        rms,
                        thdn,
                        flush=True,
                    )


# Set up measurement UPL
upl.channel.set("CH1A")  # Both channels 1+2
upl.sens[0].set("'THDN'")  # Needs quotes!!!
upl.sens[1].set("'RMS'")
upl.sens[2].set("'FREQ'")

# Set some known state on the B1 so we get (some) output
jig.set_state()

# measure_frequency_response()
