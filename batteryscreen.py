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


on(.15)
on(.15)
on(.15)
on(.15)
on(.15)
on(.15)
on(.15)
on(.15)
text_group.pop(-1)
#######setting up screen

voltage = 0
current = 0
hitemp  = 0
lotemp  = 0
hicell  = 0
locell  = 0
error   = "ISU"


# Draw voltage/current Label
vout = displayio.Group(scale=2, x=1, y=8)
vtext = """V:{:4.1f}
A:{:4.1f}""".format(voltage,current)
varea = label.Label(terminalio.FONT, text=vtext, color=0xFFFFFF)
vout.append(varea)  # Subgroup for text scaling
splash.append(vout)



#cell label
cout  = displayio.Group(scale=1, x=1, y=60)
ctext = "Hic:{:4.1f}  Loc:{:4.1f}".format(hicell,locell)
carea =  label.Label(terminalio.FONT, text=ctext, color=0xFFFFFF)
cout.append(carea)
splash.append(cout)

#temp label

tout = displayio.Group(scale=1, x=85, y=10)
ttext = """H:{:4.1f}
L:{:4.1f}
{}""".format(hitemp,lotemp,error)
tarea = label.Label(terminalio.FONT, text=ttext, color=0xFFFFFF)
tout.append(tarea)
splash.append(tout)
on(.15)
def update_display():
    global varea, carea, tarea, voltage, current, hitemp, lotemp, hicell, locell, error

    vtext = """V:{:4.1f}
A:{:4.1f}""".format(voltage,current)
    varea.text = vtext

    ctext = "Hic:{:4.1f}  Loc:{:4.1f}".format(hicell,locell)
    carea.text = ctext

    ttext = """H:{:4.1f}
L:{:4.1f}
{}""".format(hitemp,lotemp,error)
    tarea.text = ttext




while True:
    # Simulate updating variables
    voltage += 1
    current -= 0.8
    hitemp += 0.3
    lotemp += 0.6
    hicell += 0.5
    locell += 0.1

    if voltage >= 147:
        voltage = 0
        error = "voltage"
        volt_f.value= True
    if current <= -60:
        current = 0
        discharge_f.value = True
        charge_f.value = True
        error="yo mama"
    if hitemp >= 100:
        hitemp = 0
    if lotemp >= 100:
        lotemp = 0
        temp_f.value = True
    if hicell >= 100:
        hicell = 0
        error="<volt"
    if locell >= 100:
        locell = 0
        error = "volt<"
        volt_f.value= False
        discharge_f.value = False
        charge_f.value = False
        temp_f.value = False
        


    update_display()

 


