import board
import busio
import digitalio
import adafruit_rfm9x
from analogio import AnalogIn
import time
from time import sleep
import struct
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
import math
import sdcardio
import storage
import displayio
import terminalio
import adafruit_displayio_ssd1305
from adafruit_display_text import label

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
                
                            
def radioSetup():
    
    RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. 
    
    loraRESET = digitalio.DigitalInOut(board.GP8)
    loracs = digitalio.DigitalInOut(board.GP1)
    
    # Initialze RFM radio
    rfm9x = adafruit_rfm9x.RFM9x(spi, loracs, loraRESET, RADIO_FREQ_MHZ)
    
    rfm9x.tx_power = 23
    
    print("hello")
     
           
def canSetup():
    
    can_cs = digitalio.DigitalInOut(board.GP9)
    can_cs.switch_to_output()
    mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)
    
    print("hey")
               

                    
     

# Release the displays and start the clock
boot_time = time.monotonic()
displayio.release_displays()

# Initalize the SPI bus on the RP2040
# NOTE: Theses pins constant for all CAN-Pico Boards... DO NOT TOUCH
spi = busio.SPI(board.GP2, board.GP3, board.GP4)


tft_cs = board.GP22
tft_dc = board.GP23
tft_reset = board.GP21

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs,
                                 reset=tft_reset, baudrate=1000000)
display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=128, height=32,rotation=0)
FONTSCALE = 1
BORDER = 8



# Make the display context
splash = displayio.Group()
display.show(splash)

can_cs = digitalio.DigitalInOut(board.GP9)
can_cs.switch_to_output()
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)


RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. 
    
loraRESET = digitalio.DigitalInOut(board.GP8)
loracs = digitalio.DigitalInOut(board.GP1)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, loracs, loraRESET, RADIO_FREQ_MHZ)

rfm9x.tx_power = 23





sdSetup()

print(mcp)

print(mcp)

t = Timer(timeout=5)
next_message = None
message_num = 0
tire_diameter = 22
ampHours = -1
voltage = -1
mph = 0
eff = 0
current = 0
milesTraveled = 0
lowTemp = 0
highTemp = 0
avgTemp = 0
loCellV = 0
hiCellV = 0
avgCellV = 0



startTime = time.time()


time.sleep(0.2)
n=0
a="V:"+str(voltage)+" Hi:" + str(hiCellV)+ " HT:"+str(highTemp)+"\nA:"+str(current)+" Lo:" + str(loCellV)+" LT:"+str(lowTemp)

                    
text_area = label.Label(terminalio.FONT, text=a, color=0xFFFFFF)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=0,
    y=4,
)
text_group.append(text_area)

if n>=1:
    splash.pop()

splash.append(text_group)
#sleep(1)
n+=1

while True:
       
    print("-:Entering CAN Loop:-")
    """
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
    """
    # print occationally to show we're alive
    #011010110000
    
    #matches = [Match(0x600,mask = 0xFF0)]
    with mcp.listen(matches = [Match(0x6b0,mask = 0xffc)],timeout=1.0) as listener:
        message_count = listener.in_waiting()
        print("Message Count: "+ str(message_count))
        
        if message_count == 0:
            continue

        next_message = listener.receive()
        message_num = 0
        
        passno = 0
            
        while not next_message is None:
            
            
            message_count = listener.in_waiting()
            print("Message Count: "+ str(message_count))
            message_num += 1
            
            passno += 1
       
            
            
                
            if (passno>5):
                
                passno = 0
                print("Help")
                rfm9x.send(bytes("mph: "+str(mph)+"\r\n", "utf-8"))
                rfm9x.send(bytes(str(milesTraveled)+"\t"+str(ampHours)+"\r\n", "utf-8"))
                rfm9x.send(bytes(str(current)+"\t"+str(voltage)+"\r\n", "utf-8"))
                rfm9x.send(bytes(str(lowTemp)+"\r\n"+str(highTemp)+"\r\n"+str(avgTemp)+"\r\n", "utf-8"))
                rfm9x.send(bytes(str(loCellV)+"\r\n"+str(hiCellV)+"\r\n"+str(avgCellV)+"\r\n", "utf-8"))
                
                with open("/sd/BMSData.txt", "a") as f:
                    f.write(str(current)+"\r\n"+str(voltage)+"\r\n"+str(time.monotonic())+"\r\n")
                    
                with open("/sd/TempData.txt", "a") as f:
                    f.write(str(lowTemp)+"\t"+str(highTemp)+"\t"+str(avgTemp)+"\r\n"+str(time.monotonic())+"\r\n")

                with open("/sd/VoltData.txt", "a") as f:
                    f.write(str(loCellV)+"\t"+str(hiCellV)+"\t"+str(avgCellV)+"\r\n"+str(time.monotonic())+"\r\n")
                
                voltagedis = '{:,.1f}'.format(voltage)
                currentdis = '{:,.3f}'.format(current)
                hiCellVdis = '{:,.2f}'.format(hiCellV)
                loCellVdis = '{:,.2f}'.format(loCellV)
                
                
                a="V:"+str(voltagedis)+" Hi:" + str(hiCellVdis)+ " HT:"+str(highTemp)+"\nA:"+str(currentdis)+" Lo:" + str(loCellVdis)+" LT:"+str(lowTemp)
    
                                    
                text_area = label.Label(terminalio.FONT, text=a, color=0xFFFFFF)
                text_width = text_area.bounding_box[2] * FONTSCALE
                text_group = displayio.Group(
                    scale=FONTSCALE,
                    x=0,
                    y=4,
                )
                text_group.append(text_area)

                if n>=1:
                    splash.pop()

                splash.append(text_group)
                #sleep(1)
                n+=1
                            
            #print_string = "{:06.2f}".format(float(time.monotonic()-boot_time)) + "\t" + "{:05.1f}".format(voltage) + "\t"  + "{:05.1f}".format(current) + "\t"  + "{:05.1f}".format(mph)+"\t"+str(eff)
            #print(print_string,end='\t')
            """
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
            """
             # Check the id to properly unpack it
           # if next_message.id == 0x402:

                #unpack and print the message
                #holder = struct.unpack('<ff',next_message.data)
                #print(holder)
            """
            
            if next_message.id == 0x403:

                #unpack and print the message
                
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                mph = rpm*tire_diameter*math.pi*(60/63360)
                
                print(mph)
            
               
            if next_message.id == 0x40e:
            
                holder = struct.unpack('<ff',next_message.data)
                odometer = holder[0]
                milesTraveled = 0.000621371*odometer
                ampHours = holder[1]
                
                print("miles: "+str(milesTraveled)+"\t"+str(ampHours))
                #
            """ 
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
                lowTemp = holder[0]
                highTemp = holder[1]
                avgTemp = holder[2]
                
                             
                #
                print(lowTemp,highTemp,avgTemp)
            
            
                
                
            
            
                  
            if next_message.id == 0x6b2:

            #unpack and print the message
                print("volt data")
                holder = struct.unpack('>HHHBB',next_message.data)
                hiCellV = holder[0]*.0001
                loCellV = holder[1]*.0001
                avgCellV = holder[2]*.0001
                highCellVid = holder[3]
                lowCellVid = holder[4]
                
              
                
                #
                
                print(hiCellV,loCellV,avgCellV,highCellVid,lowCellVid)
                

            # Read another message why not... if no messages are avaliable None is returned
            
            next_message = listener.receive()
        
    

              
       
    
