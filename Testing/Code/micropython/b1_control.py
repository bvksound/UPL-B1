import struct

from machine import Pin, SoftSPI

WR1 = Pin(13, Pin.OUT)
RD1 = Pin(5, Pin.OUT)
ENABLE = Pin(4, Pin.OUT)

# construct a SoftSPI bus on the given pins
# polarity is the idle state of SCK
# phase=0 means sample on the first edge of SCK, phase=1 means the second
spi = SoftSPI(
    baudrate=500_000,
    polarity=1,
    phase=0,
    sck=Pin(14),
    mosi=Pin(11),
    miso=Pin(12),
    bits=8,
)


WR1 = Pin(13, Pin.OUT)
RD1 = Pin(5, Pin.OUT)
ENABLE = Pin(4, Pin.OUT)


imd_atten = False
lofilt = False
filt = False
freq_ena = False

# Should be half-way ?!
gain_adj = 2**11

freq_coarse = 0
freq_range = 0
freq_tune = 2**11
imd_gain = 2**11


def make_command_word():
    control_reg = sum(
        [1 if imd_atten else 0, 4 if lofilt else 0, 127 if freq_ena else 0]
    )
    formatting = (
        (control_reg, "CMD", 8),
        (imd_gain, "IMD-Gain", 12),
        (freq_tune, "FreqTune", 12),
        (freq_range, "FreqRange", 4),
        (freq_coarse, "FreqCoarse", 4),
        (gain_adj, "GainAdj", 12),
        (control_reg, "ControlReg", 8),
    )
    # cmd_word = (
    #    control_reg + gain_adj
    #    << 8 + freq_coarse
    #    << 20 + freq_range
    #    << 24 + freq_tune
    #    << 30 + imd_atten
    #    << 40
    # )
    # Shift in bits for board ID
    cmd_bits = "0" * 8
    # Now the IMD Atten
    cmd_bits = f"{imd_gain:012b}" + cmd_bits
    # Freq tune next
    cmd_bits = f"{freq_tune:012b}" + cmd_bits
    # Freq range
    cmd_bits = f"{freq_range:04b}" + cmd_bits
    # Freq coarse
    cmd_bits = f"{freq_coarse:04b}" + cmd_bits
    # Gain adjust
    cmd_bits = f"{gain_adj:012b}" + cmd_bits
    # Control reg last
    cmd_bits = f"{control_reg:08b}" + cmd_bits

    v = 0
    for bit in cmd_bits:
        v = v << 1
        if bit == "1":
            v |= 1
    cmd_word = struct.pack("<Q", v)
    # cmd_word = struct(
    return cmd_bits, cmd_word


def write_B1():
    bits, data = make_command_word()
    WR1.off()
    spi.write(data)
    WR1.on()
