"""
Smart Playground Distributed Embedded System
Author: Infania Pimentel
Affiliation: Tufts University CEEO
Year: 2025

Description:
Plushie node firmware. Receives routed messages, updates LED feedback, and maintains device interaction state.
"""

import time
from machine import Pin
import neopixel
from ssp_networking import SSP_Networking
from ledTasks import displayColor, turnOff

np = neopixel.NeoPixel(Pin(20), 12)
button = Pin(0, Pin.IN, Pin.PULL_UP)
networking = SSP_Networking(infmsg=True, dbgmsg=False, errmsg=True)

# Only accept from this MAC
# Replace with target device MAC address
esp2Mac = b'\xAA\xBB\xCC\xDD\xEE\xFF'

# State
receivedColor = (255, 255, 255)
lightOn = True
lastButtonState = button.value()
buttonDownTime = None
resetReady = False
inResetState = True

print("🧸 Plushie Ready")
displayColor(np, receivedColor)

while True:
    # --- Listen for color only from ESP2 when in reset state ---
    messages = networking.return_messages() or []
    for mac, msg, _ in messages:
        if mac == esp2Mac and isinstance(msg, dict) and "color" in msg:
            if inResetState:  # Only accept color when in reset state
                receivedColor = tuple(msg["color"])
                print(f"🎨 New color from ESP2: {receivedColor}")
                if lightOn:
                    displayColor(np, receivedColor)
                # Exit reset state after receiving a color
                inResetState = False
                print("🔒 Color accepted - Exiting reset mode")
            else:
                print("🔐 Ignoring color - Not in reset mode")

    # --- Button handling: short vs long press ---
    now = time.ticks_ms()
    if button.value() == 0:  # button held down
        if buttonDownTime is None:
            buttonDownTime = now
        elif time.ticks_diff(now, buttonDownTime) > 1400 and not resetReady:
            print("🔁 Long press detected — resetting to white")
            resetReady = True
            receivedColor = (255, 255, 255)
            lightOn = True
            displayColor(np, receivedColor)
            # Enter reset state after long press
            inResetState = True
            print("🔓 Entering reset mode - Ready to accept new color")
    else:
        if buttonDownTime is not None:
            if not resetReady:  # short press
                lightOn = not lightOn
                if lightOn:
                    displayColor(np, receivedColor)
                    print("💡 Light ON")
                else:
                    turnOff(np)
                    print("🌑 Light OFF")
            buttonDownTime = None
            resetReady = False

    time.sleep(0.05)

