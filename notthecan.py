import time
import struct
import digitalio
import board
import busio
import terminalio
import displayio
from adafruit_display_text import label
import adafruit_displayio_ssd1305
from adafruit_mcp2515 import MCP2515 as CAN
from adafruit_mcp2515.canio import Match

def init_display():
    """Initialize the display."""
    display_bus = displayio.FourWire(spi, command=dc, chip_select=cs,
                                     reset=reset, baudrate=1000000)
    display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=WIDTH, height=HEIGHT)
    splash = displayio.Group()
    display.root_group = splash
    return display, splash

def draw_labels(display_group):
    """Draw voltage/current, cell, and temp labels."""
    vout = displayio.Group(scale=2, x=1, y=8)
    varea = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
    vout.append(varea)
    display_group.append(vout)

    cout = displayio.Group(scale=1, x=1, y=60)
    carea = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
    cout.append(carea)
    display_group.append(cout)

    tout = displayio.Group(scale=1, x=85, y=10)
    tarea = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
    tout.append(tarea)
    display_group.append(tout)

    return varea, carea, tarea

def update_labels(varea, carea, tarea, voltage, current, hicell, locell, hitemp, lotemp, error):
    """Update the text of the labels."""
    vtext = """V:{:4.1f}
A:{:4.1f}""".format(voltage, current)
    varea.text = vtext

    ctext = "Hic:{:4.1f}  Loc:{:4.1f}".format(hicell, locell)
    carea.text = ctext

    ttext = """H:{:4.1f}
L:{:4.1f}
{}""".format(hitemp, lotemp, error)
    tarea.text = ttext

def process_message(message, voltage, current, hicell, locell, hitemp, lotemp, error):
    """Process CAN messages and update variables."""
    if message.id == 0x6b0:
        holder = struct.unpack('>hhhh', message.data)
        current = holder[1] * 0.001
        voltage = holder[3] * 0.01
    elif message.id == 0x6b1:
        holder = struct.unpack('>hhhxx', message.data)
        lotemp = holder[0]
        hitemp = holder[1]
    elif message.id == 0x6b2:
        holder = struct.unpack('>HHHBB', message.data)
        hicell = holder[0] * 0.0001
        locell = holder[1] * 0.0001
    return voltage, current, hicell, locell, hitemp, lotemp, error

def check_faults(voltage, current, hicell, locell, hitemp, lotemp, error):
    """Check for voltage, current, and temperature faults."""
    if voltage >= 126 or voltage <= 80:
        error = "PACKV"

    if hicell >= 4.19:
        error = "hicell"

    if locell <= 2.6:
        error = "locell"

    if current <= -60:
        error = "charge"

    if current >= 60:
        error = "discharge"

    if hitemp >= 60 or lotemp <= 10:
        error = "temp"
    
    return error

def on(howlong, howmany):
    """Turn LEDs on sequentially."""
    led_order = [volt_f, discharge_f, charge_f, temp_f]

    for _ in range(howmany):
        for led in led_order:
            led.value = True
            time.sleep(howlong)
        for led in led_order:
            led.value = False
            time.sleep(howlong)
        for led in reversed(led_order):
            led.value = True
            time.sleep(howlong)
        for led in reversed(led_order):
            led.value = False
            time.sleep(howlong)

def update_display(display_group, varea, carea, tarea, voltage, current, hicell, locell, hitemp, lotemp, error):
    """Update the display."""
    update_labels(varea, carea, tarea, voltage, current, hicell, locell, hitemp, lotemp, error)
    display_group.pop(-1)

spi = busio.SPI(board.GP2, board.GP3, board.GP4)
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate=500000, crystal_freq=16000000, silent=False, loopback=False)

cs = board.GP24
dc = board.GP23
reset = board.GP8
WIDTH = 128
HEIGHT = 64

display, splash = init_display()
varea, carea, tarea = draw_labels(splash)

temp = board.GP10
charge = board.GP19
discharge = board.GP20
volt = board.A3

temp_f = digitalio.DigitalInOut(temp)
temp_f.direction = digitalio.Direction.OUTPUT

charge_f = digitalio.DigitalInOut(charge)
charge_f.direction = digitalio.Direction.OUTPUT

discharge_f = digitalio.DigitalInOut(discharge)
discharge_f.direction = digitalio.Direction.OUTPUT

volt_f = digitalio.DigitalInOut(volt)
volt_f.direction = digitalio.Direction.OUTPUT

boot_time = time.time()

while True:
    with mcp.listen(matches=[Match(0x6b0, mask=0xffc)], timeout=1.0) as listener:
        message_count = listener.in_waiting()
        print("Message Count: " + str(message_count))

        if message_count == 0:
            continue

        next_message = listener.receive()
        message_num = 0

        while next_message is not None:
            voltage, current, hicell, locell, hitemp, lotemp, error = process_message(next_message, voltage, current, hicell, locell, hitemp, lotemp, error)
            error = check_faults(voltage, current, hicell, locell, hitemp, lotemp, error)
            if yeah >= 20:
                update_display(splash, varea, carea, tarea, voltage, current, hicell, locell, hitemp, lotemp, error)
                yeah = 0
            yeah += 1
            message_count = listener.in_waiting()
           

