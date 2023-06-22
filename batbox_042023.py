import board
import digitalio
import time


#Mike's fancy led
#Everbody like's blinky lights
led = digitalio.DigitalInOut(board.GP18)
led.direction = digitalio.Direction.OUTPUT

#Define Relays
motor_relay      = digitalio.DigitalInOut(board.GP22)
ground_relay     = digitalio.DigitalInOut(board.GP23)
precharge_relay  = digitalio.DigitalInOut(board.GP24)

strobe           = digitalio.DigitalInOut(board.GP25)
#Set Relays to be outputs
motor_relay.direction              = digitalio.Direction.OUTPUT
ground_relay.direction             = digitalio.Direction.OUTPUT
precharge_relay.direction          = digitalio.Direction.OUTPUT

strobe.direction                   = digitalio.Direction.OUTPUT
#Input data pins
charge_enable       = digitalio.DigitalInOut(board.GP10) 
discharge_enable    = digitalio.DigitalInOut(board.A3)
kill_car            = digitalio.DigitalInOut(board.GP19)
charge_car          = digitalio.DigitalInOut(board.GP10) #also the on/aff switch

#Set input data pins to be 
charge_enable.switch_to_input(      pull=digitalio.Pull.DOWN)
discharge_enable.switch_to_input(   pull=digitalio.Pull.DOWN)
kill_car.switch_to_input(           pull=digitalio.Pull.DOWN)
charge_car.switch_to_input(         pull=digitalio.Pull.DOWN)

#Why is this here? well idk but it's in the doccumentation  https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html#digitalio.DigitalInOut.switch_to_input
charge_enable.pull      = digitalio.Pull.DOWN 
discharge_enable.pull   = digitalio.Pull.DOWN
kill_car.pull           = digitalio.Pull.DOWN
charge_car.pull         = digitalio.Pull.DOWN #also the  on/off switch

#A silly function that is essentally a phat pause
#But it makes an led blink at 5Hz ;) 
def pause_but_blink(sleep_time:float):
    global led      
    sTime = time.time()
    while time.time() - sTime <= sleep_time: 
        led.value = not led.value
        time.sleep(0.2)

#Define a flag that is TRUE if the car has been started
started_car                = False
ok                         = True

# make sure everything is initially off to start,
ground_relay.value         = False
precharge_relay.value      = False
motor_relay.value          = False
 



'''
-----------------------------------------------------
-----------------------------------------------------
This is where the car actually runs!
'''
print(kill_car.value)
print(charge_enable.value)



#If BMS say we are good to charge and we haven't started the car yet
while not started_car:

 
    if ( not charge_enable.value and  not discharge_enable.value and not kill_car.value and not charge_car) and not started_car:
        
        print(kill_car.value)
        #Turn on the precharge relays
        ground_relay.value      = True
        precharge_relay.value   = True
            
        #Wait 5sec for precharge
        pause_but_blink(5.0)
        motor_relay.value = True
                                                    
        #now turn on shane, i mean the relay <------<         # | 
                                                       # | 
        #wait again 1sec for saftey                  |   
        pause_but_blink(1.0)                       # |    
        #LOL-----------------------------------------^
        precharge_relay.value  = False
            
            
            
        #Set the bool to TRUE to show the car has been started 
        started_car = True
        
        pause_but_blink(.2)






while started_car:

        
        
        
        
    if(( charge_enable.value or discharge_enable.value or kill_car.value or charge_car) !=0):

        ground_relay.value     = False     
        motor_relay.value      = False
        precharge_relay.value  = False
        
        
        while True:
            pause_but_blink(.75)
            strobe.toggle()
            print(charge_enable.value," = charge enable ",discharge_enable.value," = discharge enable")
            print(kill_car.value, " = kill switch "  , charge_car.value, " = on/off  " )
    
    
    print(charge_enable.value)
    pause_but_blink(.02)
    

