#!/usr/bin/env python3

# For OmniPlatform
# whill module example package for WINDOWS
# Copyright (c) 2024 WHILL, Inc.
# This software is released under the MIT License.

import time
from msvcrt import getch
from whill import ComWHILL

whill_A = ComWHILL(port='COM3')
whill_B = ComWHILL(port='COM6')

# Move forward (move backward with negative input)
def move_forward(y=0):
    actual_y = int(15 * y)
    whill_A.send_velocity(actual_y, int(0))
    whill_B.send_velocity(actual_y, int(0))

# Move right (move left with negative input)
def move_right(y=0):
    actual_y = int(15 * y)
    whill_A.send_velocity(actual_y, int(0))
    whill_B.send_velocity(-actual_y, int(0))

# Move right forward (move left backward with negative input)
def move_right_forward(y=0):
    actual_y = int(15 * y)
    whill_A.send_velocity(actual_y, int(0))
    whill_B.send_velocity(int(0), int(0))

# Move left forward (move right backward with negative input)
def move_left_forward(y=0):
    actual_y = int(15 * y)
    whill_A.send_velocity(int(0), int(0))
    whill_B.send_velocity(actual_y, int(0))

# Turn right (turn left with negative input)
def turn_right(x=0):
    actual_x = int(15 * x)
    whill_A.send_velocity(int(0), actual_x)
    whill_B.send_velocity(int(0), actual_x)

def main():
    speed_value = 20

    # Power ON
    whill_A.set_power(True)
    whill_B.set_power(True)
    time.sleep(1)

    print("--------------------------------------")
    print("Start SetVelocity command.")
    print(f"now speed: {speed_value}[%]")
    print("--------------------------------------")
    print("[↑(Up)]    : Move forward")
    print("[↓(Down)]  : Move backward")
    print("[←(Left)]  : Move left")
    print("[→(Right)] : Move right")
    print("[N]        : ↗ Move right forward")
    print("[E]        : ↘ Move right backward")
    print("[S]        : ↙ Move left backward")
    print("[W]        : ↖ Move left forward")
    print("[L]        : Turn left")
    print("[R]        : Turn right")
    print("[U]        : Up speed   +10%")
    print("[D]        : Down speed -10%")
    print("[Ctrl]+[C] : Quit")
    print("--------------------------------------")

    while True:
        key = ord(getch())
        if key == 3:
            # Ctrl + C: Exit
            print("Quit.")

            # Power OFF
            whill_A.set_power(False)
            whill_B.set_power(False)
            return
        elif key == 117:
            # u: Up speed
            speed_value += 10
            if speed_value > 100:
                speed_value = 100
            print(f"speed: {speed_value}[%]")
        elif key == 100:
            # d: Down speed
            speed_value -= 10
            if speed_value < 10:
                speed_value = 10
            print(f"speed: {speed_value}[%]")
        elif key == 108:
            # l: Turn left
            turn_right(-speed_value)
        elif key == 114:
            # r: Turn right
            turn_right(speed_value)
        elif key == 110:
            # n: Move right forward (North-east)
            move_right_forward(speed_value)
        elif key == 101:
            # e: Move right backward (south-East)
            move_left_forward(-speed_value)
        elif key == 115:
            # s: Move left backward (Sorth-west)
            move_right_forward(-speed_value)
        elif key == 119:
            # w: Move left forward (north-West)
            move_left_forward(speed_value)

        elif key == 224:
            pass
        elif key == 72:
            # Up: Move forward
            move_forward(speed_value)
        elif key == 80:
            # Down: Move backward
            move_forward(-speed_value)
        elif key == 75:
            # Left: Move left
            move_right(-speed_value)
        elif key == 77:
            # Right: Move right
            move_right(speed_value)

        else:
            # other: STOP
            print(key)
            move_forward(int(0))
            continue


if __name__ == "__main__":
    main()
