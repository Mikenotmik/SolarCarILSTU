'''

'''

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
import adafruit_ssd1325
import board
import busio
import os

boot_time = time.time()

displayio.release_displays()



can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
spi = busio.SPI(board.GP2, board.GP3, board.GP4)
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

cs = board.GP10
dc = board.GP19
reset = board.GP20
display_bus = displayio.FourWire(spi, command=dc, chip_select=cs,
                                 reset=reset, baudrate=1000000)
WIDTH = 128
HEIGHT = 64
BORDER = 0
FONTSCALE = 1
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
ampHours = -1
voltage = -1
milesTraveled = -1
tire_diameter = 22

startTime = time.time()


# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Make the display context
splash = displayio.Group()
display.show(splash)

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
text = "SOLAR CAR ISU"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)
time.sleep(3)
inner_bitmap = displayio.Bitmap(
    display.width - BORDER * 2, display.height - BORDER * 2, 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)


'''splash.pop(-1)
# Init Display Vars
up_time = time.time() - boot_time
up_time_hr = int((up_time//3600))
up_time_min = int((up_time//60)%60)
up_time_sec = int(up_time%60)'''
mph = 0
voltage = 0
current = 0
ampHours = 0
current_miles = 0
prev_miles = 0
eff = 0
odometer = 0


'''# Draw time Label
text_group = displayio.Group(scale=2, x=62, y=70)
text = "{:02d} : {:02d} : {:02d}".format(up_time_hr,up_time_min,up_time_sec)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)'''

# Draw votage/current Label
text_group = displayio.Group(scale=1, x=1, y=1)
text = "V: {:05.1f}\tA:{:05.1f}".format(voltage,current)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw Speed/effecency Label
text_group = displayio.Group(scale=2, x=1, y=1)
text = " {:4.1f} {:04.1f}".format(mph,eff)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

time.sleep(0.2)


while True:
    with mcp.listen(matches = [Match(0x400,mask=0xFF0)], timeout=0) as listener:
        eff = (mph*1000) / (current*voltage + 0.0000000001)
        print_string = "{:02d}".format(time.time()-boot_time) + "\t" + "{:05.1f}".format(voltage) + "\t"  + "{:05.1f}".format(current) + "\t"  + "{:05.1f}".format(mph)+"\t"+str(eff)
        print(print_string,end='\t')
        '''
        up_time = time.time() - boot_time
        up_time_hr = int((up_time//3600))
        up_time_min = int((up_time//60)%60)
        up_time_sec = int(up_time%60)'''


        eff = (mph*1000) / (current*voltage + 0.0000001)
        if eff> 100:
            eff=100




        screen_start = time.time()
        # Draw Speed/effecency Label
        text_group = displayio.Group(scale=1, x=5, y=15)
        text = "MPH:{:4.1f}  M/KW {:04.1f}".format(mph,eff)



        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-1] = text_group

        #print(eff,ampHours,voltage, (current_miles - prev_miles))
        prev_miles = current_miles
        new_efficiency = False

        # Draw voltage/current Label
        text_group = displayio.Group(scale=1, x=15, y=50)
        text = "V: {:04.1f}  A: {:04.1f}".format(voltage,current)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-2] = text_group

        # Draw time Label
        '''text_group = displayio.Group(scale=5, x=62, y=70)
        text = "{:02d} : {:02d} : {:02d}".format(up_time_hr,up_time_min,up_time_sec)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-3] = text_group
        print(float(time.time()-screen_start),end = '\t')'''
        
        

        
        #Here starts the new can things
        message_count = listener.in_waiting()
        print(message_count,end = '\n')
        if message_count == 0:

            continue
        
        next_message = listener.receive()
        message_num = 0

        
        while not next_message is None:
        


            message_num += 1

            # Check the id to properly unpack it
            if next_message.id == 0x402:

            #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                voltage = holder[0]
                current = holder[1]
                #print("Message From: {}: [V = {}; A = {}]".format(hex(next_message.id),voltage,current))



            if next_message.id == 0x403:
                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                mph = rpm*tire_diameter*math.pi*60*1/(12*5280)
                #print("Message From: {}: [rpm = {}; mph = {}]".format(hex(next_message.id),rpm,mph))

            next_message = listener.receive()

    




















