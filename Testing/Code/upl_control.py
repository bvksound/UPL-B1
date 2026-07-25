# Basic UPL-B1 controller using the testjig
import pyboard


class Testjig:
    def __init__(self, port):
        self.board = pyboard.Pyboard(port)
        self.board.enter_raw_repl()
        # First upload all our control code to the microcontroller
        self.board.execfile("micropython/b1_control.py")
        self.board.exec("ENABLE.on()")
        self.vars = {
            "imd_atten": False,
            "lofilt": False,
            "filt": False,
            "gain_adj": 2**11,
            "freq_range": 0,
            "freq_coarse": 0,
            "freq_tune": 2**11,
            "imd_gain": 2**11,
        }

    def check_ranges(self):
        max_12bit = 2**12
        assert -1 < self.vars["freq_range"] < max_12bit
        assert -1 < self.vars["freq_coarse"] < 16
        assert -1 < self.vars["gain_adj"] < max_12bit
        assert self.vars["filt"] in [True, False]
        assert self.vars["imd_atten"] in [True, False]
        assert self.vars["lofilt"] in [True, False]
        assert self.vars["filt"] in [True, False]

    def set_state(self):
        self.check_ranges()
        for name, value in self.vars.items():
            self.board.exec(f"{name}={value}")
        self.board.exec("write_B1()")
