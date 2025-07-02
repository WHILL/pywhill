#!/usr/bin/env python3

# whill_packet
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.


def calc_time_diff(past, current):
    diff = current - past
    if abs(diff) >= 100:
        diff = (201 - past) + current
    return diff


def s8(value):
    return -(value & 0b10000000) | (value & 0b01111111)


def parse_data_set_0(self, payload):
    speed_mode = payload[0]
    self.speed_profile[speed_mode]['forward_speed'] = payload[1]
    self.speed_profile[speed_mode]['forward_acceleration'] = payload[2]
    self.speed_profile[speed_mode]['forward_deceleration'] = payload[3]
    self.speed_profile[speed_mode]['reverse_speed'] = payload[4]
    self.speed_profile[speed_mode]['reverse_acceleration'] = payload[5]
    self.speed_profile[speed_mode]['reverse_deceleration'] = payload[6]
    self.speed_profile[speed_mode]['turn_speed'] = payload[7]
    self.speed_profile[speed_mode]['turn_acceleration'] = payload[8]
    self.speed_profile[speed_mode]['turn_deceleration'] = payload[9]
    self.seq_data_set_0 += 1
    self.fire_callback('data_set_0')

def parse_data_set_1(self, payload):
    # IMU (Accelerometer + Gyro)
    # Each axis is 16 bits (MSB + LSB), signed
    def to_signed_16(msb, lsb):
        val = (msb << 8) | lsb
        return val if val < 0x8000 else val - 0x10000

    self.imu = {}
    self.imu['acc_x'] = to_signed_16(payload[0], payload[2])  # ACC_X (MSB, LSB)
    self.imu['acc_y'] = to_signed_16(payload[4], payload[5])
    self.imu['acc_z'] = to_signed_16(payload[6], payload[7])
    self.imu['gyro_x'] = to_signed_16(payload[8], payload[9])
    self.imu['gyro_y'] = to_signed_16(payload[10], payload[11])
    self.imu['gyro_z'] = to_signed_16(payload[12], payload[13])

    # Flags
    self.low_battery_level = payload[1]
    self.enable_buzzer = payload[3]

    # Joystick
    self.joy['front'] = s8(payload[14])
    self.joy['side'] = s8(payload[15])

    # Battery
    self.battery['power'] = payload[16]
    self.battery['current'] = int.from_bytes(payload[17:19], 'big', signed=True) * 2.0

    # Motors (angle in radians? check units, current code uses *0.001)
    self.right_motor['angle'] = int.from_bytes(payload[19:21], 'big', signed=True) * 0.001
    self.left_motor['angle'] = int.from_bytes(payload[21:23], 'big', signed=True) * 0.001

    # Motors speed (unit scale from your previous code: *0.004)
    self.right_motor['speed'] = int.from_bytes(payload[23:25], 'big', signed=True) * 0.004
    self.left_motor['speed'] = int.from_bytes(payload[25:27], 'big', signed=True) * 0.004

    # Status
    self.power_status = payload[27]
    self.speed_mode_indicator = payload[28]
    self.error_code = payload[29]

    self.timestamp_past = self.timestamp_current
    self.timestamp_current = payload[30]
    self.time_diff_ms = calc_time_diff(self.timestamp_past, self.timestamp_current)

    self.seq_data_set_1 += 1
    self.fire_callback('data_set_1')

__parser_dict = {0: parse_data_set_0, 1: parse_data_set_1}


def handler(func, *args):
    return func(*args)


def dispatch_payload(self, payload):
    is_known_payload = True
    data_set_num = payload[0]
    if data_set_num in __parser_dict:
        handler(__parser_dict[data_set_num], self, payload[1:])
        self.latest_received_data_set = data_set_num
    elif data_set_num == 0x52:
        self.fire_callback('power_on')
    else:
        is_known_payload = False
    return is_known_payload
