import board
import digitalio
import time


#Mike's fancy led
led = digitalio.DigitalInOut(board.GP18)
led.direction = digitalio.Direction.OUTPUT

#Define Relays
motor_relay     = digitalio.DigitalInOut(board.GP22)
ground_relay    = digitalio.DigitalInOut(board.GP23)
precharge_relay = digitalio.DigitalInOut(board.GP24)

#Set Relays to be outputs
motor_relay.direction       = digitalio.Direction.OUTPUT
ground_relay.direction      = digitalio.Direction.OUTPUT
precharge_relay.direction   = digitalio.Direction.OUTPUT


#Input data pins
charge_enable       = digitalio.DigitalInOut(board.GP27)
discharge_enable    = digitalio.DigitalInOut(board.GP26)
kill_car            = digitalio.DigitalInOut(board.GP25)
charge_car          = digitalio.DigitalInOut(board.GP17)

#Set input data pins to be 
charge_enable.switch_to_input(      pull=digitalio.Pull.DOWN)
discharge_enable.switch_to_input(   pull=digitalio.Pull.DOWN)
kill_car.switch_to_input(           pull=digitalio.Pull.DOWN)
charge_car.switch_to_input(         pull=digitalio.Pull.DOWN)

#Why is this here? well idk but it's in the doccumentation  https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html#digitalio.DigitalInOut.switch_to_input
charge_enable.pull      = digitalio.Pull.DOWN
discharge_enable.pull   = digitalio.Pull.DOWN
kill_car.pull           = digitalio.Pull.DOWN
charge_car.pull         = digitalio.Pull.DOWN

#A silly function that is essentally a phat pause
#But it makes an led blink at 5Hz ;) 
def pause_but_blink(sleep_time:float):
    global led      
    sTime = time.time()
    while time.time() - sTime <= sleep_time: 
        led.value = not led.value
        time.sleep(0.2)

#Define a flag that is TRUE if the car has been started
started_car = False 


'''
-----------------------------------------------------
-----------------------------------------------------
This is where the car actually runs!


'''
while True:

    #If BMS say we are good to charge and we haven't started the car yet
    if (charge_enable.value and discharge_enable.value) !=1 and started_car:
        
        #Turn on the precharge relays
        ground_relay.value      = True
        precharge_relay.value   = True
        
        #Wait 5sec for precharge
        pause_but_blink(5.0)
                                                
        #now turn on shane, i mean the relay <------< 
        motor_relay.value      = True              # | 
                                                   # | 
        #wait again 1sec for saftey                  |   
        pause_but_blink(1.0)                       # |    
        #LOL-----------------------------------------^
        precharge_relay.value  = False
        
        #Set the bool to TRUE to show the car has been started 
        started_car = True
        
        
    elif((charge_enable.value and discharge_enable.value) !=0):

        ground_relay.value     = False     
        motor_relay.value      = False
        precharge_relay.value  = False

    pause_but_blink(.2)  




