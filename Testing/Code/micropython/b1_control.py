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
    cmd_word = (
        control_reg
        | ((gain_adj & 0xFFF) << 8)
        | ((freq_coarse & 0x15) << 20)
        | ((freq_range & 0x5) << 24)
        | ((freq_tune & 0xFFF) << 30)
        | ((imd_atten & 0xFFF) << 40)
    )
    cmd_bytes = struct.pack(">Q", cmd_word)
    # cmd_word = struct(
    return bin(cmd_word), cmd_bytes


def write_B1():
    bits, data = make_command_word()
    print(bits)
    WR1.off()
    spi.write(data)
    WR1.on()
