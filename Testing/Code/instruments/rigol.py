import logging
import time


class RigolScope:
    def __init__(self, rm):
        self.inst = rm.open_resource("USB0::6833::1230::DS1ZA254103299::0::INSTR")
        # self.inst.baud_rate = 115200
        # self.inst.data_bits = 8

    def set_trigger(
        self, channel, level=0, slope="POSITIVE", mode="AUTO", coupling="DC"
    ):
        self.inst.write(f":TRIG:MODE EDGE")
        self.inst.write(f":TRIG:COUPL {coupling}")
        self.inst.write(f":TRIG:SWEEP {mode}")
        self.inst.write(f":TRIG:EDGE:SOURCE CHAN{channel}")
        self.inst.write(f":TRIG:EDGE:SLOPE {slope}")
        self.inst.write(f":TRIG:EDGE:LEVEL {level}")

    def channel(self, number, coupling=None, display=True, scale=None, offset=None):
        self.inst.write(f":CHAN{number}:DISPLAY {1 if display else 0}")
        if coupling:
            self.inst.write(f":CHAN{number}:COUPLING {coupling}")
            time.sleep(0.1)
        if scale:
            self.inst.write(f":CHAN{number}:SCALe {scale}")
            time.sleep(0.1)
        if offset:
            self.inst.write(f":CHAN{number}:OFFSet {offset}")
            time.sleep(0.1)
        time.sleep(0.5)

    def clean(self):
        self.inst.write(":CLEAR")

    def autoset(self):
        logging.debug("Doing autoset...")
        self.inst.write(":AUToscale")
        time.sleep(20)

    def measure_rms(self, channel):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        #        self.inst.write(f":MEASure:ITEM VRMS,CHAN{channel}")
        response = self.inst.query(f":MEASure:ITEM? VRMS,CHAN{channel}")
        return float(response.strip())

    def measure_avg(self, channel):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        #        self.inst.write(f":MEASure:ITEM VRMS,CHAN{channel}")
        response = self.inst.query(f":MEASure:ITEM? VAVG,CHAN{channel}")
        return float(response.strip())

    def measure_freq(self, channel):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        self.inst.write(f":MEASure:COUNter CHAN{channel}")
        response = self.inst.query(":MEASure:COUNter:VALue?")
        freq = float(response.strip())
        if freq > 1e36:
            return self.measure_freq(channel)
        if freq == 0:
            response = self.inst.query(f":MEASure:ITEM? FREQ,CHAN{channel}")
            freq = float(response.strip())
        return freq
