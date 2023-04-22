import board
import busio
from analogio import AnalogIn
from time import sleep
import struct
import digitalio
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
import math


# Initalize the SPI bus on the RP2040
# NOTE: Theses pins constant for all CAN-Pico Boards... DO NOT TOUCH
cs = digitalio.DigitalInOut(board.GP9)
cs.switch_to_output()
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

reverse = digitalio.DigitalInOut(board.GP22)
reverse.pull= digitalio.Pull.UP
omega =0
forward = digitalio.DigitalInOut(board.GP23)
forward.pull = digitalio.Pull.UP

pot = AnalogIn(board.A1)
potPercent = 0

NODE_ID = 0x501

mcp = CAN(spi, cs, baudrate = 500000, crystal_freq = 16000000, silent = False)

t = Timer(timeout=5)
next_message = None
message_num = 0
tire_diameter = 22

while True:
    
    potPercent = pot.value/63500
    potPercent = pow(potPercent,1.75)
    
    if potPercent>1:
        potPercent = 1
    if potPercent<.005:
        potPercent = 0
        
    if not reverse.value :
        alpha=potPercent
        omega= - 1000
    if not forward.value:
        omega = 1000
        alpha=potPercent
    if  forward.value and  reverse.value:
        alpha = 0
        omega = 0
        
    #print(potPercent)
    #print (omega)
    
    sleep(.1)
    
    
    message = Message(id=0x501, data=struct.pack('<ff',omega,alpha), extended=False)
    send_success = mcp.send(message)
  
    with mcp.listen(matches = [Match(0x400,mask = 0xFF0)], timeout=0) as listener:
        
        
        
       
        message_count = listener.in_waiting()

        
        if message_count == 0:
           continue

        next_message = listener.receive()
        message_num = 0
        while not next_message is None:
            message_num += 1

             # Check the id to properly unpack it
            #if next_message.id == 0x402:

            #unpack and print the message
               # holder = struct.unpack('<ff',next_message.data)
                #print(holder)

            if next_message.id == 0x403:

                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                mph = rpm*tire_diameter*math.pi*(60/63360)
                print(mph)
                
            next_message = listener.receive()
            #if next_message.id == 0x40e:
            
                #holder = struct.unpack('<ff',next_message.data)
                #odometer = holder[0]
                #milesTraveled = 0.000621371*odometer
                #print("Miles = "+((str)milesTraveled))
            #ampHours = holder[1]
            #print("AmpHrs = "+ampHours)
            # Read another message why not... if no messages are avaliable None is returned
            