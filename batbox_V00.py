'''
Program for the ISU Solar Car Battery Box

Created     05/-1/24 by Mikenotmik
Last Edit   05/25/24 by NotAWildernesExplorer

UpdateLog:
    - Added error codes
    - Changed from 2 while loops to 1
    - Added some notes
    - Changed bms info to be held inside of a dictonary to simplify variables

Error Code      Fault
__________________________________________________
0               All is Good
1               Pack Voltage is outside range
2               A Cell's Voltage is outside range
3               Pack Current is outside range
4               A Battery Cell Temp is out of spec
5               CAN Timeout

'''

import board
import digitalio
import time
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
import digitalio
import busio
import struct

'''Global Variables'''
can_timeout = 2.0                                # max time between can messages till car shuts down
started     = False                              # State of the car i.e. True for on False for off
vibes_ok    = True                               # State of errors: True for good False for BAD
ISU         = 'Winners'                          # duh
car_info = {                                     # Holder for all of the usefull stuff
'HiCellV':   3.0,
'LowCellV':  3.0,
'AvgCellV':  3.0,
'HiCellVid': 1,
'LowCellVid': 1,
'HiCellT':  25.0,
'LowCellT': 25.0,
'AvgCellT': 25.0,
'PackI':     0.0, 
'PackV':   100.0
}


'''Set up the CAN'''
can_cs = digitalio.DigitalInOut(board.GP9)                                                              # Define the CS pin
can_cs.switch_to_output()                                                                               # setup the CS pin
spi = busio.SPI(board.GP2, board.GP3, board.GP4)                                                        # Init the SPI bus
mcp = CAN(spi, can_cs, baudrate = 500000, crystal_freq = 16000000, silent = False,loopback = False)     # Init CAN

'''Mike's fancy led b/c Everbody like's blinky lights'''
led = digitalio.DigitalInOut(board.GP18)            
led.direction = digitalio.Direction.OUTPUT

'''Setup Relays and Strobe'''
motor_relay      = digitalio.DigitalInOut(board.GP20)
ground_relay     = digitalio.DigitalInOut(board.GP19)
precharge_relay  = digitalio.DigitalInOut(board.GP10)
strobe           = digitalio.DigitalInOut(board.GP25)

motor_relay.direction              = digitalio.Direction.OUTPUT
ground_relay.direction             = digitalio.Direction.OUTPUT
precharge_relay.direction          = digitalio.Direction.OUTPUT
strobe.direction                   = digitalio.Direction.OUTPUT



'''Usefull functions'''                            
def read_message(message):
    '''
    Function that unpacks a can message

    Input:   canio message object
    Returns: None

    CAN ID  Orgin       unpack      data
    ____________________________________________________________________________________________________________________
    0x6b0   bms         '>hhhh'     [_,pack current,_,pack voltage]
    0x6b1   bms         '>hhhxx'    [low cell Temp, high cell temp, avg cell temp]
    0x62b   bms         '>HHHBB'    [high cell volt, low cell volt, avg cell volt, high cell volt id, low cell volt id ]
    '''


    # Check the id to properly unpack it
    if next_message.id == 0x6b0:
        holder = struct.unpack('>hhhh',next_message.data)
        car_info['PackI'] = holder[1]*.1
        car_info['PackV'] = holder[3]*.01
        
    if next_message.id == 0x6b1:
        holder = struct.unpack('>hhhxx',next_message.data)
        car_info['LowCellT']    = holder[0]
        car_info['HiCellT']     = holder[1]
        car_info['AvgCellT']    = holder[2]
    
    if next_message.id == 0x6b2:
        holder = struct.unpack('>HHHBB',next_message.data)
        car_info['HiCellV']     = holder[0]*.0001
        car_info['LowCellV']    = holder[1]*.0001
        car_info['AvgCellV']    = holder[2]*.0001
        car_info['HiCellVid']   = holder[3]
        car_info['LowCellVid']  = holder[4]

def pause_but_blink(sleep_time:float):
    '''Make blinky lights while we sleep'''
    global led 
    sTime = time.time()
    while time.time() - sTime <= sleep_time: 
        led.value = not led.value
        time.sleep(0.2)

def check_vibes():
    '''
    Check the status of the car to see if we everything is within opperating conditions

    Input:    None
    Returns: (flag,error_code)

    flag is True for eveything good
    flag is Fals for eveything bad

    error codes are at the top of doccument

    '''
    if car_info['PackV']   >= 126  or car_info['PackV']    <=80:
        return False, 1
    if car_info['HiCellV'] >= 4.19 or car_info['LowCellV'] <= 2.6:
        return False, 2
    if car_info['PackI']   <= -50  or car_info['PackI']    >= 60:
        return False, 3
    if car_info['HiCellT'] >= 60   or car_info['LowCellT'] <= 10:
        return False, 4

    return True , 0

def start_car():
    ''' 
    starts the car duh

    Inputs:     None
    Returns:    True

    I did not touch, you probably shouldn't either

    '''
    #Turn on the precharge relays
    ground_relay.value      = True
    precharge_relay.value   = True
        
    #Wait 5sec for precharge
    pause_but_blink(5.0)
    motor_relay.value = True
                                                
    #now turn on shane, i mean the relay <------<| 
    #                                            | 
    #wait again 1sec for saftey                  |   
    pause_but_blink(.50)                       # |    
    #LOL-----------------------------------------^
    precharge_relay.value  = False
        
        
        
    #Set the bool to TRUE to show the car has been started 
    return True

def stop_car(exit_code):
    '''
    Stops the car if there is any issues

    Inputs:  exit code
    Returns: NEVER, YOU NEVER LEAVE

    '''
    ground_relay.value     = False      # Turn off ground relay
    motor_relay.value      = False      # Turn off motor relay
    precharge_relay.value  = False      # Turn off precharge relay

    while True:                         # Never leave 

        for i in range(exit_code):      # Sets the number of blinks
            time.sleep(0.5)
            led.value    = not led.value        # Blink board led
            strobe.value = not strobe.value     # Blink strobe too
        time.sleep(1.0)                         # Pause so we can read the blinkn code
        print_spam()                            # Print out to terminal the car status

def print_spam():
    '''
    Spams the car info to terminal for debug:

    Input None
    Returns None

    prints 
    ['HiCellV','LowCellV','AvgCellV','HiCellVid','LowCellVid','HiCellT','LowCellT','AvgCellT','PackI','PackV',started,precharge,ground,motor relay, can message count]
    '''
    print(list(car_info.values())+[started,precharge_relay.value,ground_relay.value,motor_relay.value,message_count])


last_can_time = time.time()                                     # init timer for the last can time a can message was received
boot_time     = time.time()                                     # get the current time

'''This loop controls the car'''
while ISU == 'Winners':
    with mcp.listen(matches=[Match(0x6b0, mask=0xffc)], timeout=1.0) as listener:
        message_count = listener.in_waiting()                    # Check for messages

        if message_count == 0:
            if time.time() - last_can_time > can_timeout:        # If we haven't receved any messages, stop the car
                stop_car(5)                                      
            continue                                             # bypass what's below -> keep loop'n till we get a message

        next_message = listener.receive()                        # Load the next message in queue
        while not next_message is None:                          # Loop through the messages 
            
            message_count = listener.in_waiting()                # See how many messages we have
            read_message(next_message)                           # Read message
            print_spam()                                         # Print the car variables
        
            vibes_ok, vibe_num  =  check_vibes()                 # Check for any trouble (Warning, this function doesn't check on jim)

            if not vibes_ok:                                     # If we have a problem
                stop_car(vibe_num)                               # Stop the car

            last_can_time = time.time()                          # Reset the CAN timeout
            next_message  = listener.receive()                   # read the next message 
        
        if vibes_ok and (time.time()-boot_time > 3.0) and not started: # wait for 3 seconds after boot to start
            started = start_car()                                      # Start the car mike