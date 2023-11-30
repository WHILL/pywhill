#!/usr/bin/env python3

# whill module example package for WINDOWS
# Copyright (c) 2023 WHILL, Inc.
# This software is released under the MIT License.

import time
from msvcrt import getch
from whill import ComWHILL

whill = ComWHILL(port='COM6')
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
    print("[Ctrl]+[C] : Quit")
    print("--------------------------------------")

    while True:
        key = ord(getch())
        if key == 3:
            # Ctrl + C
            print("Quit.")
            whill.set_power(False)
            return
        elif key == 117:
            # u
            speed_value += 10
            if speed_value > 100:
                speed_value = 100
            print(f"speed: {speed_value}[%]")
        elif key == 100:
            # d
            speed_value -= 10
            if speed_value < 10:
                speed_value = 10
            print(f"speed: {speed_value}[%]")
        elif key == 106:
            # j
            control_type = 0
            print("Start 'SetJoystick' Command.")
        elif key == 118:
            # v
            control_type = 1
            print("Start 'SetVelocity' Command.")

        elif key == 224:
            pass
        elif key == 72:
            # Up
            drive_motor(speed_value, int(0))
        elif key == 80:
            # Down
            drive_motor(-1 * speed_value, int(0))
        elif key == 75:
            # Left
            drive_motor(int(0), -1 * speed_value)
        elif key == 77:
            # Right
            drive_motor(int(0), speed_value)

        else:
            # other: STOP
            print(key)
            drive_motor(int(0), int(0))
            continue


if __name__ == "__main__":
    main()
