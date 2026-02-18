"""
Smart Playground Distributed Embedded System
Author: Infania Pimentel
Affiliation: Tufts University CEEO
Year: 2025

Description:
Relay node firmware. Coordinates message routing between devices, manages connection logic, and ensures state synchronization across nodes.
"""

import time
from machine import Pin
import neopixel
from ssp_networking import SSP_Networking
from ledTasks import displayColor, turnOff

np = neopixel.NeoPixel(Pin(20), 12)
networking = SSP_Networking(infmsg=True, dbgmsg=False, errmsg=True)
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Replace with target device MAC address
esp1Mac = b'\xAA\xBB\xCC\xDD\xEE\xFF'# ← update with ESP1's actual MAC

hasBroadcast = False
wasButtonDown = False
receivedColor = None
ackSent = False
echoMode = True

#Just received message from ESP1 about color... auto start the rainbow in ESP1 code... but once button is released AND color rexeived by at least one rexeiving ESP3, then indicate the reset, AKA the mailbox reset...



print("📦 ESP2 Ready")
displayColor(np, (255, 255, 255))

while True:
    # 1. Check for incoming messages
    messages = networking.return_messages() or []

    for mac, msg, _ in messages:
        if isinstance(msg, dict) and "color" in msg:
            receivedColor = tuple(msg["color"])
            print(f"🎨 Color received: {receivedColor}")
            displayColor(np, (0, 0, 255))  # blue flash
            networking.send(mac, {"ack": True})
            ackSent = True

        elif isinstance(msg, int) and echoMode:
            networking.send(mac, msg)
            print(f"🔁 Echoed: {msg}")

    # 2. If button is pressed, stop echoing and broadcast color
    if ackSent and button.value() == 0:
        print("🚪 Door closed. Broadcasting color...")
        echoMode = False
        if receivedColor:
            networking.broadcast({"color": list(receivedColor)})
            displayColor(np, (0, 255, 0))  # green confirmation
            time.sleep(2)
            displayColor(np, (255, 255, 255))  # reset to white
        receivedColor = None
        ackSent = False
        echoMode = True
        hasBroadcast = True

    # 3. Detect release AFTER broadcast and send reset
    if button.value() == 1 and wasButtonDown and hasBroadcast:
        print("📨 Button released — sending RESET to ESP1...")
        time.sleep(0.1)  # debounce
        networking.send(esp1Mac, {"reset": True})
        hasBroadcast = False
        wasButtonDown = False

    # 4. Update button state
    if button.value() == 0:
        wasButtonDown = True

    time.sleep(0.1)

