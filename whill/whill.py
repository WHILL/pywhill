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
    """
    WHILL mobility device control interface.
    
    This class provides methods to communicate with and control WHILL mobility devices
    through serial communication. It supports joystick control, velocity control,
    power management, speed profile configuration, and battery monitoring.
    
    Attributes:
        com (serial.Serial): Serial communication object for WHILL device.
        joy (whill_data.Joy): Current joystick input values from WHILL controller.
        speed_profile (whill_data.SpeedProfile): Speed profile settings for different modes.
        right_motor (whill_data.Motor): Right motor status (angle, speed).
        left_motor (whill_data.Motor): Left motor status (angle, speed).
        battery (whill_data.Battery): Battery status information.
        power_status (int): Current power status of the device.
        speed_mode_indicator (int): Current speed mode indicator.
        error_code (int): Error code from the device.
    """

    class CommandID(IntEnum):
        START = 0
        STOP = auto()
        SET_POWER = auto()
        SET_JOYSTICK = auto()
        SET_SPEED_PROFILE = auto()
        SET_BATTERY_VOLTAGE_OUT = auto()
        SET_BATTERY_SAVING = auto()
        RESERVE_2 = auto()
        SET_VELOCITY = auto()

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
        CommandID.SET_BATTERY_SAVING: 3,
        CommandID.SET_VELOCITY: 6,
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
        self.power_status = 0
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
        self.thread = None
        self.__stop_event = threading.Event()
        self.__hold_control_type = None  # 'joy' or 'velocity'

    def register_callback(self, event, func=None):
        """
        Register a callback function for specific events.
        
        Parameters:
            event (str): Event type ('data_set_0', 'data_set_1', 'power_on')
            func (callable): Callback function to register
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        ret = False
        if event in self.__callback_dict:
            self.__callback_dict[event] = func
            ret = True
        return ret

    def fire_callback(self, event):
        if self.__callback_dict[event] is not None:
            return self.__callback_dict[event]()

    def refresh(self):
        """
        Refresh device data by reading and processing incoming serial data.
        
        Reads all available data from the serial port, validates it, and updates
        internal state variables including joystick, motor, and battery data.
        
        Returns:
            bool: True if new data was received and processed, False otherwise
        """
        is_refreshed = False
        self.power_status = 0
        self.error_code = 0
        while self.com.in_waiting > 0:
            data_length, payload = self.receive_data()
            if data_length > 0:
                if self.validate_received_data(data_length, payload):
                    if wp.dispatch_payload(self, payload):
                        is_refreshed = True
        return is_refreshed

    def sleep(self, secs, step_sec=0.01):
        """
        Sleep for specified duration while continuously refreshing device data.
        
        This method is useful for maintaining communication with the device
        during idle periods.
        
        Parameters:
            secs (float): Total sleep duration in seconds
            step_sec (float): Interval between refresh calls in seconds
        """
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
        """
        Send joystick control command to the WHILL device.
        
        Controls the mobility device movement using joystick-style input.
        Positive front values move forward, negative move backward.
        Positive side values turn right, negative turn left.
        
        Parameters:
            front (int): Forward/backward joystick value (-100 to 100)
            side (int): Left/right joystick value (-100 to 100)
            
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_JOYSTICK, self.UserControl.DISABLE, front, side]
        return self.send_command(command_bytes)

    def send_velocity(self, front=0, side=0):
        """
        Send velocity control command to the WHILL device.
        
        Controls the mobility device movement using direct velocity commands.
        This provides more precise control than joystick commands.
        
        Parameters:
            front (int): Forward/backward velocity value (-500 to 1500)
            side (int): Left/right velocity value (-750 to 750)
            
        Returns:
            int: Number of bytes written to serial port
        """
        front_up = (front & 0xFF00) >> 8
        front_low = (front & 0x00FF)
        side_up = (side & 0xFF00) >> 8
        side_low = (side & 0x00FF)
        command_bytes = [self.CommandID.SET_VELOCITY, self.UserControl.DISABLE, front_up, front_low, side_up, side_low]
        return self.send_command(command_bytes)

    def send_stop(self):
        return self.send_joystick()

    def release_joystick(self):
        command_bytes = [self.CommandID.SET_JOYSTICK, self.UserControl.ENABLE, 0, 0]
        return self.send_command(command_bytes)

    def start_data_stream(self, interval_msec, data_set_number=1, speed_mode=5):
        """
        Start continuous data streaming from the WHILL device.
        
        Begins receiving periodic status updates including joystick, motor,
        and battery data at the specified interval.
        
        Parameters:
            interval_msec (int): Data update interval in milliseconds (10-65535)
            data_set_number (int): Data set number (0 or 1)
            speed_mode (int): Speed mode setting (0-5) only data_set_number=0 is valid
                - 0-3: speed modes for joystick control
                - 4: speed mode for serial control
                - 5: speed mode for smart-phone app control
            
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.START, data_set_number, interval_msec >> 8, interval_msec & 0xFF, speed_mode]
        return self.send_command(command_bytes)

    def stop_data_stream(self):
        """
        Stop continuous data streaming from the WHILL device.
        
        Halts the periodic status updates started by start_data_stream().
        
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.STOP]
        return self.send_command(command_bytes)

    def send_power_on(self):
        """
        Send power on command to the WHILL device.
        
        Powers on the mobility device control system. Sends the command twice
        with a 200ms delay to ensure reliable activation.
        
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_POWER, self.PowerCommand.ON]
        self.send_command(command_bytes)
        time.sleep(0.200)
        return self.send_command(command_bytes)

    def send_power_off(self):
        """
        Send power off command to the WHILL device.
        
        Powers off the mobility device control system.
        
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_POWER, self.PowerCommand.OFF]
        return self.send_command(command_bytes)

    def set_power(self, power_state_command):
        """
        Set power state of the WHILL device.
        
        Convenience method to power on or off the device based on boolean input.
        
        Parameters:
            power_state_command (bool): True to power on, False to power off
            
        Returns:
            int: Number of bytes written to serial port
        """
        if power_state_command:
            return self.send_power_on()
        else:
            return self.send_power_off()

    def set_speed_profile(self, speed_mode,
                          forward_speed_max, forward_accel, forward_decel,
                          reverse_speed_max, reverse_accel, reverse_decel,
                          turn_speed_max,    turn_accel,    turn_decel):
        """
        Set speed profile parameters for a specific speed mode.
        
        Configures acceleration, deceleration, and maximum speed settings
        for forward, reverse, and turning movements.
        
        Parameters:
            speed_mode (int): Speed mode to configure (0-5)
                - 0-3: speed modes for joystick control
                - 4: speed mode for serial control
                - 5: speed mode for smart-phone app control
            forward_speed_max (int): Maximum forward speed (8-60)
            forward_accel (int): Forward acceleration rate (10-64)
            forward_decel (int): Forward deceleration rate (40-160)
            reverse_speed_max (int): Maximum reverse speed (8-30)
            reverse_accel (int): Reverse acceleration rate (10-50)
            reverse_decel (int): Reverse deceleration rate (40-80)
            turn_speed_max (int): Maximum turning speed (8-35)
            turn_accel (int): Turning acceleration rate (10-60)
            turn_decel (int): Turning deceleration rate (40-160)
            
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_SPEED_PROFILE,
                         speed_mode,
                         forward_speed_max, forward_accel, forward_decel,
                         reverse_speed_max, reverse_accel, reverse_decel,
                         turn_speed_max,    turn_accel,    turn_decel]
        return self.send_command(command_bytes)

    def set_speed_profile_via_dict(self, speed_mode, profile):
        """
        Set speed profile using a dictionary of parameters.
        
        Convenience method to set speed profile using a dictionary format
        instead of individual parameters.
        
        Parameters:
            speed_mode (int): Speed mode to configure (0-5)
                - 0-3: speed modes for joystick control
                - 4: speed mode for serial control
                - 5: speed mode for smart-phone app control
            profile (dict): Dictionary containing speed profile parameters:
                - forward_speed: Maximum forward speed (8-60)
                - forward_acceleration: Forward acceleration rate (10-64)
                - forward_deceleration: Forward deceleration rate (40-160)
                - reverse_speed: Maximum reverse speed (8-30)
                - reverse_acceleration: Reverse acceleration rate (10-50)
                - reverse_deceleration: Reverse deceleration rate (40-80)
                - turn_speed: Maximum turning speed (8-35)
                - turn_acceleration: Turning acceleration rate (10-60)
                - turn_deceleration: Turning deceleration rate (40-160)
                
        Returns:
            bool: True if speed_mode is valid and command sent, False otherwise
        """
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
        """
        Set battery voltage output mode.
        
        Enables or disables battery voltage output for monitoring purposes.
        
        Parameters:
            vbatt_on_off (int): 1 to enable, 0 to disable battery voltage output
            
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_BATTERY_VOLTAGE_OUT, vbatt_on_off]
        return self.send_command(command_bytes)

    def set_battery_saving(self, low_battery_level=19, sounds_buzzer=True):
        """
        Configure battery saving mode settings.
        
        Sets the low battery threshold and buzzer behavior for battery saving mode.
        
        Parameters:
            low_battery_level (int): Battery level threshold for saving mode (1-90)
            sounds_buzzer (bool): Whether to sound buzzer when battery is low
            
        Returns:
            int: Number of bytes written to serial port
        """
        command_bytes = [self.CommandID.SET_BATTERY_SAVING, low_battery_level, sounds_buzzer]
        return self.send_command(command_bytes)

    def hold_core(self, control_type, front, side, timeout=1000):
        while self.__timeout_count < timeout:
            if self.__stop_event.is_set():
                self.__timeout_count = self.__TIMEOUT_MAX + 1
                self.__stop_event.clear()
            self.__timeout_count += 100  # millisecond
            # print(self.__timeout_count)
            
            if control_type == 'joy':
                self.send_joystick(front=front, side=side)
            elif control_type == 'velocity':
                self.send_velocity(front=front, side=side)
            
            time.sleep(0.10)
        else:
            self.__timeout_count = 0
            self.__hold_control_type = None

    def unhold(self):
        """
        Stop any ongoing hold operation.
        
        Signals the hold thread to stop and clears the stop event.
        """
        self.__stop_event.set()

    def unhold_joy(self):
        self.unhold()

    def unhold_velocity(self):
        self.unhold()

    def hold_joy(self, front, side, timeout=1000):
        """
        Hold joystick control values for a specified duration.
        
        Continuously sends the specified joystick values until timeout is reached
        or unhold() is called. This method runs in a separate thread.
        
        Parameters:
            front (int): Forward/backward joystick value (-100 to 100)
            side (int): Left/right joystick value (-100 to 100)
            timeout (int): Hold duration in milliseconds (max 60000)
        """
        if self.thread and self.thread.is_alive():
            self.unhold()
            self.thread.join()
        self.__stop_event.clear()
        if timeout > self.__TIMEOUT_MAX:
            print('Timeout must be equal to or less than {timeout_max}'.format(timeout_max=self.__TIMEOUT_MAX))
            timeout = self.__TIMEOUT_MAX
        self.__timeout_count = 0
        self.__hold_control_type = 'joy'
        self.thread = threading.Thread(target=self.hold_core, kwargs={'control_type': 'joy', 'front': front, 'side': side, 'timeout': timeout})
        self.thread.start()

    def hold_velocity(self, front, side, timeout=1000):
        """
        Hold velocity control values for a specified duration.
        
        Continuously sends the specified velocity values until timeout is reached
        or unhold() is called. This method runs in a separate thread.
        
        Parameters:
            front (int): Forward/backward velocity value (-500 to 1500)
            side (int): Left/right velocity value (-750 to 750)
            timeout (int): Hold duration in milliseconds (max 60000)
        """
        if self.thread and self.thread.is_alive():
            self.unhold()
            self.thread.join()
        self.__stop_event.clear()
        if timeout > self.__TIMEOUT_MAX:
            print('Timeout must be equal to or less than {timeout_max}'.format(timeout_max=self.__TIMEOUT_MAX))
            timeout = self.__TIMEOUT_MAX
        self.__timeout_count = 0
        self.__hold_control_type = 'velocity'
        self.thread = threading.Thread(target=self.hold_core, kwargs={'control_type': 'velocity', 'front': front, 'side': side, 'timeout': timeout})
        self.thread.start()
