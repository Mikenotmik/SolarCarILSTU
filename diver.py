import board
import busio
import math
import struct
import time
import analogio
import digitalio
import displayio
import terminalio
import adafruit_ssd1325
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_display_text import label

# Release the displays and start the clock
boot_time = time.monotonic()
displayio.release_displays()

# Create the SPI Buss
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

# Set up the MCP 2515 on the SPI Bus
can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)

# Set up the OLED on the SPI Bus
cs = board.GP22
dc = board.GP23
reset = board.GP21
WIDTH = 128
HEIGHT = 64
BORDER = 0
FONTSCALE = 1

display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
display = adafruit_ssd1325.SSD1325(display_bus, width=WIDTH, height=HEIGHT)
display.brightness = 1.0



startTime = time.time()
# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] =0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

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
time.sleep(2.5)
splash.pop(-1)




tire_diameter = 22
mph     = 0
voltage = 0
current = 0
eff     = 0

# Draw Speed/effecency Label
text_group = displayio.Group(scale=3, x=3, y=12)
text = "S: {:04.1f}".format(mph)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw Effecency Label
text_group = displayio.Group(scale=3, x=3, y=41)
text = "E: {:04.1f}".format(eff)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Draw voltage/current Label
text_group = displayio.Group(scale=1, x=15, y=60)
text = "V: {:04.1f}  A: {:04.1f}".format(voltage,current)
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

time.sleep(0.2)


while True:
    with mcp.listen(timeout=0) as listener:
        eff = (mph*1000) / (current*voltage + 0.000001) 
        eff = 99.99 if eff > 99.9 else eff


        print_string = "{:06.2f}".format(float(time.monotonic()-boot_time)) + "\t" + "{:05.1f}".format(voltage) + "\t"  + "{:05.1f}".format(current) + "\t"  + "{:05.1f}".format(mph)+"\t"+str(eff)
        print(print_string,end='\t')



        # Draw Speed Label
        text_group = displayio.Group(scale=3, x=3, y=12)
        text = "S: {:04.1f}".format(mph)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-3] = text_group

        # Draw Effecency Label
        text_group = displayio.Group(scale=3, x=3, y=41)
        text = "E: {:04.1f}".format(eff)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-2] = text_group

        # Draw voltage/current Label
        text_group = displayio.Group(scale=1, x=15, y=60)
        text = "V: {:04.1f}  A: {:04.1f}".format(voltage,current)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
        text_group.append(text_area)  # Subgroup for text scaling
        splash[-1] = text_group




        #Here starts where we do the CAN things
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

            next_message = listener.receive(
