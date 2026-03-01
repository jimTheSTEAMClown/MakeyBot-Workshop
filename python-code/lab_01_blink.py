# ============================================================
# Lab 01 - Blink: Hello, GPIO!
# MakeyBot Workshop - STEAM Clown's Workshops
# ============================================================
# Source: STEAM Clown - www.steamclown.org 
# GitHub: https://github.com/jimTheSTEAMClown/MakeyBot-Workshop
# Hacker: Jim Burnham - STEAM Clown, Engineer, Maker, Propmaster & Adrenologist 
# This example code is licensed under the CC BY-NC-SA 4.0, GNU GPL and EUPL
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# https://www.gnu.org/licenses/gpl-3.0.en.html
# https://eupl.eu/
# Program/Design Name:		lab_01_blink.py
# Description:    Blink an LED
# Revision: 
#  Revision 0.02 - Updated 2026/02/28 with Template comments
#  Revision 0.01 - Created 2026/02/28
# Additional Comments: 
# Dependencies:   
#   python3
#   Hardware:
#       Using BOARD reference to I/O Pins
#       Physical pin 11 --> 330Ω resistor --> LED (+) --> LED (-) --> GND (pin 9)
#   Library: gpiozero
#       Install: pre-installed on Raspberry Pi OS
#       Docs:    https://gpiozero.readthedocs.io/
#   Run with:
#       python3 lab_01_blink.py
#   Stop with:
#       Ctrl + C
# ============================================================

from gpiozero import LED
import time

# --- Setup ---
# Create an LED object connected to physical pin 11 (BOARD numbering).
# gpiozero uses "BOARD" prefix strings for physical pin numbers.
# Physical pin 11 = BCM GPIO17
led = LED("BOARD11")

print("Lab 01 - Blink starting...")
print("Press Ctrl+C to stop.\n")

# --- Main Loop ---
# Blink the LED on and off forever
try:
    while True:
        led.on()
        print("LED ON")
        time.sleep(0.5)        # Stay on for 0.5 seconds

        led.off()
        print("LED OFF")
        time.sleep(0.5)        # Stay off for 0.5 seconds

except KeyboardInterrupt:
    # Runs when the user presses Ctrl+C
    print("\nStopped by user.")
    led.off()                  # Make sure LED is off when we exit
