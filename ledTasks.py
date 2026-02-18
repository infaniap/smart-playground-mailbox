"""
Smart Playground Distributed Embedded System
Author: Infania Pimentel
Affiliation: Tufts University CEEO
Year: 2025

Description:
LED state management and animation utilities for distributed embedded nodes.
Implements pairing feedback, idle states, status indicators, and dynamic effects.
"""

import time, math

def hsv2rgb(hue, s=1.0, v=1.0):
    hue = hue % 360
    c = v * s
    x = c * (1 - abs((hue / 60) % 2 - 1))
    m = v - c

    if 0 <= hue < 60:
        r, g, b = c, x, 0
    elif 60 <= hue < 120:
        r, g, b = x, c, 0
    elif 120 <= hue < 180:
        r, g, b = 0, c, x
    elif 180 <= hue < 240:
        r, g, b = 0, x, c
    elif 240 <= hue < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

def animatePairing(np, delay=0.05, baseColor=(0, 0, 255)):
    trailLength = 4  # number of LEDs in trail
    brightnessLevels = [0.8, 0.5, 0.3, 0.1]

    for i in range(np.n):
        for j in range(trailLength):
            index = (i - j) % np.n
            brightness = brightnessLevels[j]
            np[index] = tuple(int(c * brightness) for c in baseColor)
        np[(i - trailLength) % np.n] = (0, 0, 0)
        np.write()
        time.sleep(delay)

def breathing(np, speed=0.05, color=(0, 0, 255), steps=20):
    for i in range(steps):
        brightness = int((i / steps) * 255)
        dimmedColor = tuple(int(c * brightness / 255) for c in color)
        np.fill(dimmedColor)
        np.write()
        time.sleep(speed)

    for i in reversed(range(steps)):
        brightness = int((i / steps) * 255)
        dimmedColor = tuple(int(c * brightness / 255) for c in color)
        np.fill(dimmedColor)
        np.write()
        time.sleep(speed)
        
def blinking(np, amt, colorChoice, speed):
    for i in range(amt):
        displayColor(np, colorChoice)
        time.sleep(speed)
        turnOff(np)
        time.sleep(speed)

def singleStatusPoint(np, amt, colorChoice):
    np.fill((0, 0, 0))
    n = np.n
    spacing = n // amt 
    for i in range(amt):
        index = (i*spacing) % n
        np[index] = colorChoice        
    np.write()

def trailingRainbow(np, speed):

    def wheel(pos):
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        elif pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        else:
            pos -= 170
            return (0, int(pos * 3), int(255 - pos * 3))

    numPixels = np.n
    offset = 0

    for _ in range(numPixels):  # run for one full rotation
        for i in range(numPixels):
            pixelIndex = (i + offset) % 256
            np[i] = wheel((pixelIndex * 256 // numPixels) % 256)
        np.write()
        time.sleep(speed)
        offset = (offset + 1) % 256
    
    
def updateOLED(oled, msg, color=(0,0,0)):
    oled.fill(0)
    oled.text(msg, 0, 0)
    oled.text(f"R:{color[0]}", 0, 20)
    oled.text(f"G:{color[1]}", 0, 30)
    oled.text(f"B:{color[2]}", 0, 40)
    oled.show()

def displayColor(np, color):
    for i in range(np.n):
        np[i] = color
    np.write()

def reset2Idle(np, oled):
    displayColor(np, (0, 0, 0))
    updateOLED(oled, "IDLE")
    
def turnOff(np):
    displayColor(np, (0, 0, 0))


