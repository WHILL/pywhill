#!/usr/bin/env python3

# whill
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import serial
import threading
import time
from enum import IntEnum, auto
from . import whill_data as wd
from . import whill_packet as wp


class ComWHILL():

    class CommandID(IntEnum):
        START = 0
        STOP = auto()
        SET_POWER = auto()
        SET_JOYSTICK = auto()
        SET_SPEED_PROFILE = auto()
        SET_BATTERY_VOLTAGE_OUT = auto()

    class UserControl(IntEnum):
        DISABLE = 0
        ENABLE = auto()

    class PowerCommand(IntEnum):
        OFF = 0
        ON = auto()

    __CMD_LENGTH_TABLE = {
        CommandID.START: 5,
        CommandID.SET_POWER: 2,
        CommandID.SET_JOYSTICK: 4,
        CommandID.SET_SPEED_PROFILE: 11,
        CommandID.SET_BATTERY_VOLTAGE_OUT: 2,
    }

    __PROTOCOL_SIGN = 0xAF

    def __init__(self, port, timeout=None):
        """
        Initialize WHILL class object

        Parameters
        ----------
        port (str): Device name of a serial port for communicating to WHILL.
        timeout (int): Set a read timeout value for serial object.

        Attributes
        ----------
        com (serial.Serial): Serial object for communicating to WHILL.
        virtual_joy (whill_data.Joy): Currently unused.
        joy (whill_data.Joy): Input value from WHILL's joystick controller.
        speed_profile (whill_data.SpeedProfile): Speed profile array for six settings.
        right_motor (whill_data.Motor): Right motor status (angle, speed).
        left_motor (whill_data.Motor): Left motor status (angle, speed).
        """
        self.com = serial.Serial(port=port, baudrate=38400, timeout=timeout)
        self.virtual_joy = wd.Joy()
        self.joy = wd.Joy()
        self.speed_profile = wd.SpeedProfile()
        self.right_motor = wd.Motor()
        self.left_motor = wd.Motor()
        self.battery = wd.Battery()
        self.power_status = False
        self.speed_mode_indicator = 0
        self.error_code = 0
        self.timestamp_past = 0
        self.timestamp_current = 0
        self.time_diff_ms = 0
        self.seq_data_set_0 = 0
        self.seq_data_set_1 = 0
        self.latest_received_data_set = 0
        self.__callback_dict = {'data_set_0': None, 'data_set_1': None, 'power_on': None}
        self.__timeout_count = 0
        self.__TIMEOUT_MAX = 60000 # 60 seconds
        self.thread = threading.Thread(target=self.hold_joy_core, kwargs={'front': 0, 'side': 0, 'timeout': 1000})
        self.__stop_event = threading.Event()

    def register_callback(self, event, func=None):
        ret = False
        if event in self.__callback_dict:
            self.__callback_dict[event] = func
            ret = True
        return ret

    def fire_callback(self, event):
        if self.__callback_dict[event] is not None:
            return self.__callback_dict[event]()

    def refresh(self):
        is_refreshed = False
        while self.com.in_waiting > 0:
            data_length, payload = self.receive_data()
            if data_length > 0:
                if self.validate_received_data(data_length, payload):
                    if wp.dispatch_payload(self, payload):
                        is_refreshed = True
        return is_refreshed

    def sleep(self, secs, step_sec=0.01):
        current_sec = 0
        while current_sec < secs:
            self.refresh()
            time.sleep(step_sec)
            current_sec += step_sec

    def receive_data(self):
        data_length = -1
        payload = []
        read_byte = int.from_bytes(self.com.read(size=1), 'big', signed=False)
        if read_byte == self.__PROTOCOL_SIGN:
            data_length = int.from_bytes(self.com.read(size=1), 'big', signed=False)
            payload = self.com.read(size=data_length)
        return data_length, payload

    def validate_received_data(self, data_length, payload):
        checksum = 0
        checksum ^= self.__PROTOCOL_SIGN
        checksum ^= data_length
        for x in payload:
            checksum ^= x
        if checksum == 0:
            is_valid = True
        else:
            is_valid = False
        return is_valid

    def send_command(self, payload):
        length = self.__CMD_LENGTH_TABLE[payload[0]]
        command_bytes = [self.__PROTOCOL_SIGN, length + 1]
        command_bytes.extend(payload)
        checksum = 0
        for i, x in enumerate(command_bytes):
            if x < 0:
                x = int.from_bytes(x.to_bytes(length=1, byteorder='big', signed=True), byteorder='big', signed=False)
                command_bytes[i] = x
            checksum ^= x
        command_bytes.append(checksum)
        # print(command_bytes)
        return self.com.write(bytes(command_bytes))

    def send_joystick(self, front=0, side=0):
        command_bytes = [self.CommandID.SET_JOYSTICK, self.UserControl.DISABLE, front, side]
        return self.send_command(command_bytes)

    def send_stop(self):
        return self.send_joystick()

    def release_joystick(self):
        command_bytes = [self.CommandID.SET_JOYSTICK, self.UserControl.ENABLE, 0, 0]
        return self.send_command(command_bytes)

    def start_data_stream(self, interval_msec, data_set_number=1, speed_mode=5):
        command_bytes = [self.CommandID.START, data_set_number, interval_msec >> 8, interval_msec & 0xFF, speed_mode]
        return self.send_command(command_bytes)

    def stop_data_stream(self):
        command_bytes = [self.CommandID.STOP]
        return self.send_command(command_bytes)

    def send_power_on(self):
        command_bytes = [self.CommandID.SET_POWER, self.PowerCommand.ON]
        self.send_command(command_bytes)
        time.sleep(0.200)
        return self.send_command(command_bytes)

    def send_power_off(self):
        command_bytes = [self.CommandID.SET_POWER, self.PowerCommand.OFF]
        return self.send_command(command_bytes)

#    def set_power(self, power_state_command):
#        command_bytes = [self.CommandID.SET_POWER, power_state_command]
#        return self.send_command(command_bytes)

    def set_speed_profile(self, speed_mode,
                          forward_speed_max, forward_accel, forward_decel,
                          reverse_speed_max, reverse_accel, reverse_decel,
                          turn_speed_max,    turn_accel,    turn_decel):
        command_bytes = [self.CommandID.SET_SPEED_PROFILE,
                         speed_mode,
                         forward_speed_max, forward_accel, forward_decel,
                         reverse_speed_max, reverse_accel, reverse_decel,
                         turn_speed_max,    turn_accel,    turn_decel]
        return self.send_command(command_bytes)

    def set_speed_profile_via_dict(self, speed_mode, profile):
        ret = False
        if speed_mode in range(0, 6):
            self.set_speed_profile(speed_mode,
                                  profile['forward_speed'],
                                  profile['forward_acceleration'],
                                  profile['forward_deceleration'],
                                  profile['reverse_speed'],
                                  profile['reverse_acceleration'],
                                  profile['reverse_deceleration'],
                                  profile['turn_speed'],
                                  profile['turn_acceleration'],
                                  profile['turn_deceleration'])
            ret = True
        return ret

    def set_battery_voltage_output_mode(self, vbatt_on_off):
        command_bytes = [self.CommandID.SET_BATTERY_VOLTAGE_OUT, vbatt_on_off]
        return self.send_command(command_bytes)

    def hold_joy_core(self, front, side, timeout=1000):
        while self.__timeout_count < timeout:
            if self.__stop_event.is_set():
                self.__timeout_count = self.__TIMEOUT_MAX + 1
                self.__stop_event.clear()
            self.__timeout_count += 100  # millisecond
            # print(self.__timeout_count)
            self.send_joystick(front=front, side=side)
            time.sleep(0.10)
        else:
            self.__timeout_count = 0

    def unhold_joy(self):
        self.__stop_event.set()

    def hold_joy(self, front, side, timeout=1000):
        if self.thread.is_alive():
            self.unhold_joy()
            self.thread.join()
        self.__stop_event.clear()
        if timeout > self.__TIMEOUT_MAX:
            print('Timeout must be equal to or less than {timeout_max}'.format(timeout_max=self.__TIMEOUT_MAX))
            timeout = self.__TIMEOUT_MAX
        self.__timeout_count = 0
        self.thread = threading.Thread(target=self.hold_joy_core, kwargs={'front': front, 'side': side, 'timeout': timeout})
        self.thread.start()
