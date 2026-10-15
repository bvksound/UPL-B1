#!/usr/bin/env python
from Gpib import *
from gpib import GpibError


class Fluke45:
    def __init__(self, addr=12):
        self.dev = Gpib(0, addr, timeout=50)
        self.command("AUTO")

    def query(self, cmd, length=512):
        self.dev.write(cmd)
        return self.dev.read(length).decode("latin-1").strip()

    def command(self, cmd):
        self.query(f"{cmd};*OPC?")

    def measure_volt(self):
        self.command("ADC")

    def rate(self, rate):
        assert rate in "SMF"
        self.command("RATE {rate}")

    def read_display(self):
        return self.query("VAL1?")
