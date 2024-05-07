import board
import busio
import analogio
import digitalio
import time

import struct
import math
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
import digitalio
import board
import busio
import board
import terminalio
import displayio
from adafruit_display_text import label
import adafruit_displayio_ssd1305
import board
import busio
import os





boot_time = time.time()

displayio.release_displays()



can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
spi = busio.SPI(board.GP2, board.GP3, board.GP4)
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

cs = board.GP24
dc = board.GP23
reset = board.GP8
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs,
                                 reset=reset, baudrate=1000000)
WIDTH = 128
HEIGHT = 64
BORDER = 0
FONTSCALE = 1
display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=WIDTH, height=HEIGHT)



# Make the display context



splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)




# Draw a smaller inner rectangle



inner_bitmap = displayio.Bitmap(
    display.width - BORDER * 2, display.height - BORDER * 2, 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

# Draw a label



text = "you are special."
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)


# Subgroup for text scaling


splash.append(text_group)

temp       = board.GP10
charge     = board.GP19
discharge  = board.GP20
volt       = board.A3

#Initialize

temp_f = digitalio.DigitalInOut(temp)
temp_f.direction = digitalio.Direction.OUTPUT

charge_f = digitalio.DigitalInOut(charge)
charge_f.direction = digitalio.Direction.OUTPUT

discharge_f= digitalio.DigitalInOut(discharge)
discharge_f.direction = digitalio.Direction.OUTPUT

volt_f = digitalio.DigitalInOut(volt)
volt_f.direction = digitalio.Direction.OUTPUT

def on(y):
    
    volt_f.value= True
    time.sleep(y)
    discharge_f.value = True
    time.sleep(y)
    charge_f.value = True
    time.sleep(y)

    temp_f.value = True
    time.sleep(y)

    volt_f.value= False
    time.sleep(y)
    discharge_f.value = False
    time.sleep(y)
    charge_f.value = False
    time.sleep(y)

    temp_f.value = False
    time.sleep(y)

time.sleep(2)
text_group.pop(-1)





# Draw voltage/current Label
vout = displayio.Group(scale=2, x=1, y=8)
vtext = """V:114.6
A:12.98"""#.format(voltage,current)
varea = label.Label(terminalio.FONT, text=vtext, color=0xFFFFFF)
vout.append(varea)  # Subgroup for text scaling
splash.append(vout)

time.sleep(0.2)

#cell label
cout  = displayio.Group(scale=1, x=1, y=60)
ctext = "hic:  loc:"
carea =  label.Label(terminalio.FONT, text=ctext, color=0xFFFFFF)
cout.append(carea)
splash.append(cout)

#temp label

tout = displayio.Group(scale=1, x=90, y=6)
ttext = """h:
l:

ISU"""
tarea = label.Label(terminalio.FONT, text=ttext, color=0xFFFFFF)
tout.append(tarea)
splash.append(tout)


while True:
    on(.05)
    pass
