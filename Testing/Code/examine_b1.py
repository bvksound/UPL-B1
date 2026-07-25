import time

import pyvisa

from instruments.hameg import HamegScope
from upl_control import Testjig

rm = pyvisa.ResourceManager()

scope = HamegScope(rm, "/dev/ttyUSB0")
jig = Testjig("/dev/ttyACM0")

for freq_range in [0, 1, 2, 4]:
    jig.vars["freq_range"] = freq_range
    for coarse in range(16):
        jig.vars["freq_coarse"] = coarse
        for gain in range(0, 0x1000, 0x1FF):
            jig.vars["gain_adj"] = gain
            jig.vars["imd_gain"] = gain
            for tune in range(0, 0x1000, 0x1FF):
                jig.vars["freq_tune"] = tune
                jig.set_state()
                time.sleep(0.1)
                # Measure an average of five samples
                freqs = [scope.measure_freq(2) for _ in range(5)]
                freq = sum(freqs) / len(freqs)
                print(freq_range, coarse, gain, tune, freq, flush=True)
