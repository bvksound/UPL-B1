import logging
import time

import numpy as np


class RigolScope:
    def __init__(self, rm):
        self.inst = rm.open_resource("USB0::6833::1230::DS1ZA254103299::0::INSTR")
        # self.inst.baud_rate = 115200
        # self.inst.data_bits = 8

    def read_binary(self):
        # Pull the exact unparsed byte array straight out of the USB buffer
        raw_bytes = self.inst.read_raw()
        logging.debug(f"Bytes received from self.inst: {len(raw_bytes)}")

        # 5. Manually slice away Rigol's IEEE 488.2 block header
        # Format is '#9000001200...' where 9 implies a 9-digit length descriptor
        if raw_bytes.startswith(b"#"):
            header_length = 2 + int(chr(raw_bytes[1]))  # Typically 11 bytes total
            waveform_data = raw_bytes[header_length:]

            # Trim off any occasional trailing characters if they exist
            if waveform_data.endswith(b"\n"):
                waveform_data = waveform_data[:-1]

            logging.debug(
                f"Successfully recovered {len(waveform_data)} raw trace points."
            )
            return waveform_data
        else:
            logging.error(
                "Error: Received data does not match an IEEE binary block format."
            )

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

    def timebase(self, scale, left=False):
        self.inst.write(f":TIMebase:MAIN:SCALe {scale}")
        if left:
            # The scope has 6 graticules to the left of 0, so 5 is a good guess
            offset = 5 * scale
            self.inst.write(f":TIMebase:MAIN:OFFSET {offset}")

    def run(self):
        self.inst.write(":RUN")

    def read_waveform(self, channel):
        self.inst.write(":STOP")
        self.inst.write(f":WAV:SOUR CHAN{channel}")
        self.inst.write(":WAV:MODE NORM")
        self.inst.write(":WAV:FORM BYTE")
        yinc = float(self.inst.query(":WAVeform:YINCrement?"))
        xinc = float(self.inst.query(":WAVeform:XINCrement?"))
        yorigin = float(self.inst.query(":WAVeform:YORigin?"))
        self.inst.write(":WAV:DATA?")
        time.sleep(0.5)  # Give the Rigol processor a moment to buffer
        raw_data = self.read_binary()
        wave = np.frombuffer(raw_data, dtype=np.uint8)
        wave = wave.astype("f")
        wave = wave - 127
        wave = wave * yinc
        self.run()
        return xinc, wave

    def clean(self):
        self.inst.write(":CLEAR")

    def autoset(self):
        logging.debug("Doing autoset...")
        self.inst.write(":AUToscale")
        time.sleep(20)

    def measure_rms(self, channel, tries=3):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        #        self.inst.write(f":MEASure:ITEM VRMS,CHAN{channel}")
        response = self.inst.query(f":MEASure:ITEM? VRMS,CHAN{channel}")
        value = float(response.strip())
        if value > 1e32 and tries:
            time.sleep(0.5)
            return self.measure_rms(channel, tries - 1)
        return value

    def measure_avg(self, channel, tries=3):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        #        self.inst.write(f":MEASure:ITEM VRMS,CHAN{channel}")
        response = self.inst.query(f":MEASure:ITEM? VAVG,CHAN{channel}")
        value = float(response.strip())
        if value > 1e32 and tries:
            time.sleep(0.5)
            return self.measure_rms(channel, tries - 1)
        return value

    def measure_freq(self, channel):
        #        self.inst.write(f":MEASure:SOURce CHAN{channel}")
        self.inst.write(f":MEASure:COUNter CHAN{channel}")
        response = self.inst.query(":MEASure:COUNter:VALue?")
        try:
            freq = float(response.strip())
        except ValueError:
            return -1
        if freq == 0:
            response = self.inst.query(f":MEASure:ITEM? FREQ,CHAN{channel}")
            freq = float(response.strip())
        return freq
