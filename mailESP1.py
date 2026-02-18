"""
Smart Playground Distributed Embedded System
Author: Infania Pimentel
Affiliation: Tufts University CEEO
Year: 2025

Description: Mailbox node firmware. Handles user input (slider/button), manages local LED state, and initiates communication events to the relay node.

"""

# === ESP1: Mailbox UI (Color Selector) ===
import machine, neopixel, time
from machine import Pin, ADC
from ssp_networking import SSP_Networking
from ledTasks import hsv2rgb, displayColor, turnOff, breathing, trailingRainbow



# Networking
networking = SSP_Networking(infmsg=True, dbgmsg=False, errmsg=True)


# NeoPixel setup
np = neopixel.NeoPixel(machine.Pin(2), 12)
n = np.n


# Slider for color
slider = ADC(Pin(5))
slider.atten(ADC.ATTN_11DB)

# Button
button = Pin(9, Pin.IN, Pin.PULL_UP)
print("Button at boot:", button.value())

# Networking setup
# Replace with target device MAC address
esp2Mac = b'\xAA\xBB\xCC\xDD\xEE\xFF'


# State
wakeUp = False
sleeping = True
sliderSleep = True
colorSelectionActive = False
lastSliderActivityTime = 0
sliderThreshold = 10
finalColor = (255, 255, 255)
lockedColor = (255, 255, 255)
lastSliderVal =  0
colorLocked = False
ackReceived = False

#Button Handler
def buttonHandler(pin):
    global wakeUp, sleeping, colorSelectionActive, colorLocked, finalColor, lockedColor, ackReceived
    
    sleeping = False
    if button.value() == 0: 
        if not wakeUp:
            print("Waking Up....")
            wakeUp = True
            sleeping = False
            
        elif colorSelectionActive and not colorLocked:
            colorLocked = True
            lockedColor= finalColor
            print("Locked Color:", lockedColor)
            ackReceived = False      
            
button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=buttonHandler)

#While in sleep mode
def enterSleepMode():
    turnOff(np)
    print("ESP1 is sleeping...")

def potSleepMode():
    breathing(np, speed=0.05, color=(255, 255, 255), steps=10)


def waitForSlider():
    global wakeUp, colorSelectionActive, lastSliderActivityTime, lastSliderVal
    
    print("waiting for slider movement")
    lastSliderVal = slider.read()
    
    while wakeUp and not colorSelectionActive:        
        #Breathing until slider is moved
        print("Breathing while waiting for slider movement...")
        potSleepMode()
        currentSliderVal = slider.read()

        if abs(currentSliderVal - lastSliderVal) > sliderThreshold:
            #If slider is moved
            print("Slider moved")
            colorSelectionActive = True
            #wakeUp = False
            lastSliderActivityTime = time.time()
        lastSliderVal = currentSliderVal
        time.sleep(0.1)        
        
def colorSelection():
    global colorSelectionActive, colorLocked, finalColor, lastSliderActivityTime, lastSliderVal, wakeUp

    currentSliderVal = slider.read()
    #Get the color from the slider
    hue = (currentSliderVal / 4095) * 360
    finalColor = hsv2rgb(hue)
    displayColor(np, finalColor)
    
    # Detect slider movement
    if abs(currentSliderVal - lastSliderVal) > sliderThreshold:
        lastSliderActivityTime = time.time()

    # Inactivity timeout: 3 seconds
    if time.time() - lastSliderActivityTime > 3:
        print("⏱️ No slider movement — returning to breathing mode")
        colorSelectionActive = False
        wakeUp = True  # Back to breathing mode
        #potSleepMode()

    lastSliderVal = currentSliderVal
    
    
def displayLockedColor():
    global lockedColor
    displayColor(np, lockedColor)
    
    
def sendLockedColor():
    global lockedColor, ackReceived
    
    print("📡 Sending locked color to ESP2...")
    try:
        networking.send(esp2Mac, {"color": list(lockedColor)})
        print(f"🚀 Sent: {lockedColor}")
    
    except Exception as e:
        print("Send failed:", e)
    time.sleep(0.5)
    messages = networking.return_messages() or []
    for _, msg, _ in messages:
        if isinstance(msg, dict) and msg.get("ack") == True:
            print("✅ ACK received from ESP2")
            ackReceived = True
            break
def waitForDoorClose():
    global networking
    print("🕓 Waiting for ESP2 echo to stop (door close)...")

    echoCount = 0
    lastEcho = -1
    stableCount = 0
    timeoutLimit = 10  # seconds
    silenceThreshold = 3  # how many missed echoes in a row before assuming door closed
    startTime = time.time()

    while time.time() - startTime < timeoutLimit:
        # Send an echo
        networking.echo(esp2Mac, echoCount)
        print(f"📡 Sent echo count: {echoCount}")
        echoCount += 1

        time.sleep(0.5)

        messages = networking.return_messages() or []

        receivedEcho = False
        for _, msg, _ in messages:
            if isinstance(msg, int):
                print(f"🔁 Received echo: {msg}")
                if msg == lastEcho:
                    stableCount += 1
                else:
                    stableCount = 0
                lastEcho = msg
                receivedEcho = True
                break

        if not receivedEcho:
            stableCount += 1
            print("⚠️ No echo received")

        if stableCount >= silenceThreshold:
            print("🚪 Door closed — no more echo from ESP2")
            return True

    print("⌛ Timeout reached — assuming door is closed")
    return True

    
        
    
def handleReset():
    global wakeUp, sleeping, colorSelectionActive, colorLocked, ackReceived

    print("🌈 Playing rainbow animation...")
    trailingRainbow(np, speed=0.1)

    print("🔁 Resetting state...")
    wakeUp = False
    sleeping = True
    colorSelectionActive = False
    colorLocked = False
    ackReceived = False

def Main():
    global wakeUp, sleeping, lastSliderActivityTime, colorSelectionActive, finalColor
    
    lastSliderVal = slider.read()
    while True:
        # Check if in sleep mode
        if sleeping:
            enterSleepMode()
            time.sleep(0.1)
            print("sleepingStep complete")
            continue
        #If  waking up
        if wakeUp and not colorSelectionActive:
            waitForSlider()       
       #Handle color selection        
        elif colorSelectionActive and not colorLocked:
            colorSelection()
            print("colorSelection complete")
        #Locked the color and sending to ESP2    
        elif colorSelectionActive and colorLocked and not ackReceived:
            displayLockedColor()
            print("displayLockedColor complete")
            sendLockedColor()
            print("sendLockedColor complete")
            
        # Got ACK, now wait for door close and reset
        elif colorSelectionActive and colorLocked and ackReceived:
            print("ACK received, waiting for door close...")
            waitForDoorClose()
            handleReset()
        
        messages = networking.return_messages() or []
        for _, msg, _ in messages:
            if isinstance(msg, dict) and msg.get("reset") == True:
                print("🔁 RESET message received from ESP2")
                handleReset()
            
        time.sleep(0.1)
            
Main()
