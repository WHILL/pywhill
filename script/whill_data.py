#!/usr/bin/env python3

# whill_data
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

class Data3D(dict):
    def __init__(self):
        super().__init__()
        self.update({'x': 0})
        self.update({'y': 0})
        self.update({'z': 0})


class Joy(dict):
    def __init__(self):
        super().__init__()
        self.update({'front': 0})
        self.update({'side': 0})


class SpeedProfile(list):
    class Element(dict):
        def __init__(self):
            super().__init__()
            self.update({'forward_speed': 0})
            self.update({'forward_acceleration': 0})
            self.update({'forward_deceleration': 0})

            self.update({'reverse_speed': 0})
            self.update({'reverse_acceleration': 0})
            self.update({'reverse_deceleration': 0})

            self.update({'turn_speed': 0})
            self.update({'turn_acceleration': 0})
            self.update({'turn_deceleration': 0})

    def __init__(self):
        self.mode_1 = self.Element()
        self.mode_2 = self.Element()
        self.mode_3 = self.Element()
        self.mode_4 = self.Element()
        self.mode_remote = self.Element()
        self.mode_cr = self.Element()
        list.__init__(self,
                      [self.mode_1,
                       self.mode_2,
                       self.mode_3,
                       self.mode_4,
                       self.mode_remote,
                       self.mode_cr])


class Battery(dict):
    def __init__(self):
        super().__init__()
        self.update({'level': 0})
        self.update({'current': 0.0})


class Motor(dict):
    def __init__(self):
        super().__init__()
        self.update({'angle': 0.0})
        self.update({'speed': 0.0})
