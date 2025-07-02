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
    def to_signed_16(msb, lsb):
        val = (msb << 8) | lsb
        return val if val < 0x8000 else val - 0x10000

    self.imu = {}
    self.imu_acc['x'] = to_signed_16(payload[0], payload[1]) * 0.122  # [mg]
    self.imu_acc['y'] = to_signed_16(payload[2], payload[3]) * 0.122  # [mg]
    self.imu_acc['z'] = to_signed_16(payload[4], payload[5]) * 0.122  # [mg]
    self.imu_gyro['x'] = to_signed_16(payload[6], payload[7]) * 4.375  # [mdps]
    self.imu_gyro['y'] = to_signed_16(payload[8], payload[9]) * 4.375  # [mdps]
    self.imu_gyro['z'] = to_signed_16(payload[10], payload[11]) * 4.375  # [mdps]

    self.joy['front'] = s8(payload[12])
    self.joy['side'] = s8(payload[13])

    self.battery['level'] = payload[14]
    self.battery['current'] = to_signed_16(payload[15], payload[16]) * 2.0  # [mA]

    self.right_motor['angle'] = - to_signed_16(payload[17], payload[18]) * 0.001  # [rad]
    self.left_motor['angle'] = to_signed_16(payload[19], payload[20]) * 0.001

    self.right_motor['speed'] = - to_signed_16(payload[21], payload[22]) * 0.004  # [km/h]
    self.left_motor['speed'] = to_signed_16(payload[23], payload[24]) * 0.004

    self.power_status = payload[25]
    self.speed_mode_indicator = payload[26]
    self.error_code = payload[27]
    self.angle_detect_counter = payload[28]

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
