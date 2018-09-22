#!/usr/bin/env python3

# whill_packet
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

def calc_time_diff(past, current):
    diff = current - past
    if abs(diff) >= 100:
        diff = (201 - past) + current
    return diff

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
    self.accelerometer['x'] = int.from_bytes(payload[0:1], 'big', signed=True) * 0.122
    self.accelerometer['y'] = int.from_bytes(payload[2:3], 'big', signed=True) * 0.122
    self.accelerometer['z'] = int.from_bytes(payload[4:5], 'big', signed=True) * 0.122
    self.gyro['x'] = int.from_bytes(payload[6:7], 'big', signed=True) * 4.375
    self.gyro['y'] = int.from_bytes(payload[8:9], 'big', signed=True) * 4.375
    self.gyro['z'] = int.from_bytes(payload[10:11], 'big', signed=True) * 4.375
    self.joy['front'] = payload[12]
    self.joy['side'] = payload[13]
    self.battery['level'] = payload[14]
    self.battery['current'] = int.from_bytes(payload[15:16], 'big', signed=True) * 2.0
    self.right_motor['angle'] = int.from_bytes(payload[17:18], 'big', signed=True) * 0.001
    self.left_motor['angle'] = int.from_bytes(payload[19:20], 'big', signed=True) * 0.001
    self.right_motor['speed'] = int.from_bytes(payload[21:22], 'big', signed=True) * 0.004
    self.left_motor['speed'] = int.from_bytes(payload[23:24], 'big', signed=True) * 0.004
    self.power_status = payload[25]
    self.speed_mode_indicator = payload[26]
    self.error_code = payload[27]

    self.timestamp_past = self.timestamp_current
    self.timestamp_current = s8(payload[28])
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
