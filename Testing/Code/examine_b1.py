import time

import pyvisa

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

freq = 0


def measure_settling_time(freq_range, coarse, gain, tune):
    rigol.set_trigger(3, level=0.1, slope="POSITIVE", mode="NORMAL")
    rigol.clear()
    jig.vars["freq_range"] = freq_range
    jig.vars["gain"] = gain
    jig.vars["freq_coarse"] = coarse
    jig.vars["tune"] = tune
    jig.set_state()
    # Now we


# Set some known state on the B1 so we get (some) output
jig.set_state()

# Set up scope, first
rigol.set_trigger(1, 0, slope="POSITIVE", mode="AUTO")
rigol.channel(1, "DC", display=True, scale=1, offset=0)
rigol.channel(2, "DC", display=True, scale=1, offset=0)
rigol.channel(3, "DC", display=True, scale=0.5, offset=0)
rigol.channel(4, "DC", display=True, scale=0.5, offset=0)

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
                while not (1 < freq < 1e6):
                    freq = rigol.measure_freq(1)
                time.sleep(100 / freq)
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
