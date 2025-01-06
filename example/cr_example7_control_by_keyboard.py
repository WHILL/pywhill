#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2025 WHILL, Inc.
# This software is released under the MIT License.

import time
from readchar import readkey, key
from whill import ComWHILL

whill = ComWHILL(port='COM3')
control_type = 0  # 0: Joystick / 1: Velocity

def drive_motor(y=0, x=0):
    global control_type
    if control_type == 0:
        whill.send_joystick(y, x)
    else:
        actual_x = int(7.5 * x)
        actual_y = 0
        if y > 0:
            actual_y = int(15 * y)
        else:
            actual_y = int(5 * y)
        whill.send_velocity(actual_y, actual_x)

def main():
    whill.set_power(True)
    time.sleep(1)

    speed_value = 20
    
    global control_type
    control_type = 0

    print("Start SetJoystick command.")
    print(f"now speed: {speed_value}[%]")
    print("--------------------------------------")
    print("[↑(Up)]    : Move forward")
    print("[↓(Down)]  : Move backwards")
    print("[←(Left)]  : Turn left")
    print("[→(Right)] : Turn right")
    print("[U]        : Up speed   +10%")
    print("[D]        : Down speed -10%")
    print("[J]        : Use SetJoystick command")
    print("[V]        : Use SetVelocity command")
    print("[Q]        : Quit")
    print("--------------------------------------")

    while True:
        k = readkey()
        if k == 'q':
            print("Quit.")
            whill.set_power(False)
            return
        elif k == 'u':
            speed_value += 10
            if speed_value > 100:
                speed_value = 100
            print(f"speed: {speed_value}[%]")
        elif k == 'd':
            speed_value -= 10
            if speed_value < 10:
                speed_value = 10
            print(f"speed: {speed_value}[%]")
        elif k == 'j':
            control_type = 0
            print("Start 'SetJoystick' Command.")
        elif k == 'v':
            control_type = 1
            print("Start 'SetVelocity' Command.")
        elif k == key.UP:
            # Up
            drive_motor(speed_value, int(0))
        elif k == key.DOWN:
            # Down
            drive_motor(-1 * speed_value, int(0))
        elif k == key.LEFT:
            # Left
            drive_motor(int(0), -1 * speed_value)
        elif k == key.RIGHT:
            # Right
            drive_motor(int(0), speed_value)
        else:
            # other: STOP
            print(k)
            drive_motor(int(0), int(0))
            continue


if __name__ == "__main__":
    main()
