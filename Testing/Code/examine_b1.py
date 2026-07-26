import time

import pyvisa

from instruments.hameg import HamegScope
from instruments.rigol import RigolScope
from upl_control import Testjig

rm = pyvisa.ResourceManager()

rigol = RigolScope(rm)
# hameg = HamegScope(rm, "/dev/ttyUSB0")
jig = Testjig("/dev/ttyACM0")

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
                # freqs = [hameg.measure_freq(2) for _ in range(5)]
                # freq = sum(freqs) / len(freqs)

                # Let the hardware settle for a bit (50 waves at least)
                while not (1 < freq < 1e6):
                    freq = rigol.measure_freq(1)
                time.sleep(50 / freq)
                freq = rigol.measure_freq(1)

                rms = [rigol.measure_rms(ch) for ch in [3, 4]]
                if max(rms) > 1e36:
                    rigol.autoset()
                rms = [rigol.measure_rms(ch) for ch in [1, 2, 3, 4]]
                avg = [rigol.measure_avg(ch) for ch in [1, 2, 3, 4]]
                print(
                    freq_range,
                    coarse,
                    gain,
                    tune,
                    freq,
                    *rms,
                    *avg,
                    flush=True,
                )
