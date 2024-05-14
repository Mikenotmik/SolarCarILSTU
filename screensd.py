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


def sdSetup():
    
    sdcs = board.GP24
    sdcard = sdcardio.SDCard(spi, sdcs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    
    
    with open("/sd/GeneralData.txt", "w") as f:
        f.write("Current\tVoltage\tElapsed Time\r\n")
    
    with open("/sd/TempData.txt", "w") as f:
        f.write("Low Temp\tHigh Temp\tAvg Temp\tElapsed Time\r\n")
        
    with open("/sd/VoltData.txt", "w") as f:
        f.write("Low Cell Volt\tHigh Cell Volt\tAvg Cell Volt\tElapsed Time\r\n")

        
    print("hi") 

can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
spi = busio.SPI(board.GP2, board.GP3, board.GP4)
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

sdSetup()


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


def on(howlong, howmany):
    """Turn LEDs on sequentially (forward), then turn them off sequentially, and finally reverse the order multiple times."""
    led_order = [volt_f, discharge_f, charge_f, temp_f]

    for _ in range(howmany):
        # Forward sequence: turn on LEDs in order
        for led in led_order:
            led.value = True
            time.sleep(howlong)

        # Forward sequence: turn off LEDs in order
        for led in led_order:
            led.value = False
            time.sleep(howlong)

        # Reverse sequence: turn on LEDs in reverse order
        for led in reversed(led_order):
            led.value = True
            time.sleep(howlong)

        # Reverse sequence: turn off LEDs in reverse order
        for led in reversed(led_order):
            led.value = False
            time.sleep(howlong)


on(.05,1)

yeah = 0

text_group.pop(-1)
#######setting up screen

voltage = 100
current = 0
hitemp  = 25
lotemp  = 25
hicell  = 3
locell  = 3
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



on(.05,4)






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



            
       
 

    # print occationally to show we're alive
    #011010110000
    
    #matches = [Match(0x600,mask = 0xFF0)]
start = time.monotonic()

while True:
    with mcp.listen(matches=[Match(0x6b0, mask=0xffc)], timeout=1.0) as listener:
        message_count = listener.in_waiting()
        print("Message Count: " + str(message_count))

        if message_count == 0:
            continue

        next_message = listener.receive()
        message_num = 0

        while not next_message is None:
            # Handle message processing here

            # Read another message
            next_message = listener.receive()


                        # Voltage faults
            if voltage >= 126 or voltage <=80:
                error = "PACKV"
                volt_f.value= True
            
            if hicell >= 4.19:

                error="hicell"
                volt_f.value= True
            
            if locell <= 2.6:

                error = "locell"
                volt_f.value= True
              
            
            #Current faults
            if current <= -60:
            
                charge_f.value = True
                error="charge"
            
            
            if current >= 60:
            
                charge_f.value = True
                error="discharge"
            
            
            
            if hitemp >= 60:
                
                temp_f.value = True
            
            if lotemp <= 10:
        
                temp_f.value = True
            if yeah >=20:
                
                update_display()
                yeah = 0
            
            yeah +=1
            message_count = listener.in_waiting()
            print("Message Count: "+ str(message_count))
            message_num += 1
            
    
                            
    
            # Check the id to properly unpack it
            if next_message.id == 0x6b0:
                print("BMS Data")
            #unpack and print the message
                holder = struct.unpack('>hhhh',next_message.data)
                current = holder[1]*.001
                voltage = holder[3]*.01
                
                  
                    
                #
                print(current,voltage)
            
               
            
            
            if next_message.id == 0x6b1:
                print("temps")
                
                #logTime = time()
                #unpack and print the message
                holder = struct.unpack('>hhhxx',next_message.data)
                lotemp = holder[0]
                hitemp = holder[1]
                
                
                             
                #
                print(lotemp,hitemp)
            
            
                
                
            
            
                  
            if next_message.id == 0x6b2:

            #unpack and print the message
                print("volt data")
                holder = struct.unpack('>HHHBB',next_message.data)
                hicell = holder[0]*.0001
                locell = holder[1]*.0001
                
                
              
                
            
                
                print(hicell,locell)
                
                
                if time.monotonic()-start >= 1:
                    start = time.monotonic()
                    
                    with open("/sd/BMSData.txt", "a") as f:
                        f.write(str(current)+"\r\n"+str(voltage)+"\r\n"+str(time.monotonic())+"\r\n")
                        
                    with open("/sd/TempData.txt", "a") as f:
                        f.write(str(lowTemp)+"\t"+str(highTemp)+"\t"+str(avgTemp)+"\r\n"+str(time.monotonic())+"\r\n")

                    with open("/sd/VoltData.txt", "a") as f:
                        f.write(str(loCellV)+"\t"+str(hiCellV)+"\t"+str(avgCellV)+"\r\n"+str(time.monotonic())+"\r\n")
                    
            
            # Read another message why not... if no messages are avaliable None is returned
            
            next_message = listener.receive()
