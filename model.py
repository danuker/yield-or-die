#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yield or Die! Train yourself to learn rules for right-of-way,
without spending lots of money for practice at driving school!
Copyright (C) 2021 Dan Gheorghe Haiduc (aka danuker)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.audio import SoundLoader

from yield_resolver import must_yield, relative_position

from time import time
import random
import os


class StretchyImage(Image):
    allow_stretch=BooleanProperty(True)


def signal_turn(source_road, target_road):
    """
    Tell the signal
    >>> signal_turn('left', 'behind')
    'sig_right'
    >>> signal_turn('left', 'ahead')
    'sig_left'
    >>> signal_turn('left', 'right')
    'sig_no'
    >>> signal_turn('right', 'behind')
    'sig_left'
    >>> signal_turn('right', 'ahead')
    'sig_right'
    >>> signal_turn('behind', 'ahead')
    'sig_no'
    >>> signal_turn('ahead', 'left')
    'sig_right'

    >>> signal_turn('behind', 'behind')
    Traceback (most recent call last):
     ...
    ValueError: U-turns not allowed.
    """

    directions = ['behind', 'left', 'ahead', 'right']
    signals = [None, 'sig_left', 'sig_no', 'sig_right']

    source_i = directions.index(source_road)
    target_i = directions.index(target_road)

    sig_i = (target_i - source_i) % len(signals)
    sig = signals[sig_i]

    if sig:
        return sig
    else:
        raise ValueError('U-turns not allowed.')


class Car(StretchyImage):
    angle = NumericProperty(0)
    images = {
        'sig_no': 'pics/pngs/car.png',
        'sig_left': 'pics/pngs/car_signal_left.png',
        'sig_right': 'pics/pngs/car_signal_right.png'
    }

    def __init__(self, source_road, target_road, app, **kwargs):
        StretchyImage.__init__(self, **kwargs)

        self.source = self.images['sig_no']

        self.app = app
        self.intersection = self.app.game.intersection

        # Strings that name the road
        self.source_road = source_road
        self.target_road = target_road
        self.stop_time = float('inf')
        self.signal = signal_turn(source_road, target_road)

    def must_yield(self, other_cars, prios):
        for other_car in other_cars:
            rel = relative_position(
                self.source_road, other_car.source_road
            )

            must_yield_now, reason = must_yield(
                my_right_of_way=prios[self.source_road],
                my_turn=self.signal,
                other_right_of_way=prios[other_car.source_road],
                other_turn=other_car.signal,
                other_relative_position=rel
            )

            if must_yield_now:
                return must_yield_now, reason

        # We don't have to yield to anyone in the intersection
        return False, \
            "Other cars either won't cross your path,\nnor need to yield to you."

    def blink(self, state):
        if state:
            self.source = self.images[self.signal]
        else:
            self.source = self.images['sig_no']

    def update(self):
        """Place car on screen"""
        if self.intersection.touch_start_y:
            self.blink(True)
            if self.stop_time == float('inf'):
                self.stop_time = time()
            return
        else:
            # Time the blink-lights
            if int(time() * 2) % 2 == 0:
                self.blink(True)
            else:
                self.blink(False)

        center_x = self.intersection.width / 2
        center_y = self.intersection.height / 2
        speed = min(self.intersection.width, self.intersection.height)/100
        now = min(self.stop_time, time())
        dist_from_center = center_x - (now - self.intersection.time)*speed
        lane = self.app.lane_width/2

        car_coords = {
            'left': [
                center_x - dist_from_center,
                center_y - lane
            ],
            'right': [
                center_x + dist_from_center,
                center_y + lane
            ],
            'behind': [
                center_x + lane,
                center_y - dist_from_center
            ],
            'ahead': [
                center_x - lane,
                center_y + dist_from_center
            ]
        }

        self.center = car_coords[self.source_road]

        angles = {
            'left': -90, 'ahead': 180, 'right': 90, 'behind': 0,
        }
        self.angle = angles[self.source_road]


class PlayerCar(Car):
    def __init__(self, source_road, target_road, app, **kwargs):
        Car.__init__(self, source_road, target_road, app, **kwargs)
        self.images = {
            'sig_no': 'pics/pngs/player.png',
            'sig_left': 'pics/pngs/player_signal_left.png',
            'sig_right': 'pics/pngs/player_signal_right.png'
        }


class Sign(Widget):
    def __init__(self, app, name, facing, with_panel, **kwargs):
        """
        app : app having intersection as "game" field
        name : 'yield' or 'prio'
        facing : 'left', 'right', 'ahead', or 'behind'
        with_panel : True or False
        """
        super(Sign).__init__(**kwargs)
        self.app = app
        self.intersection = self.app.game.intersection

        self.name = name
        self.facing = facing
        self.with_panel = with_panel

        if facing in ['left', 'right']:
            facing = f"ahead-{facing}"

        self.sign = StretchyImage(source=f'pics/pngs/sign-{name}-{facing}.png')
        if self.facing == 'behind':
            self.panel_pics = self.build_panel_map()

        else:
            self.panel_pics = [
                StretchyImage(source=f'pics/pngs/panel-{facing}.png')
            ]
        self.pole = StretchyImage(source='pics/pngs/pole.png')

        if facing != 'behind':
            self.app.game.add_widget(self.sign)
            self.add_panel_map()
        self.app.game.add_widget(self.pole)
        if facing == 'behind':
            self.app.game.add_widget(self.sign)
            self.add_panel_map()

    def build_panel_map(self):
        panels = [
            StretchyImage(source='pics/pngs/panel-blank.png'),
        ]

        for road, has_prio in self.intersection.prios.items():
            kind = 'prio' if has_prio else 'yield'

            panels.append(
                StretchyImage(source=f'pics/pngs/panel-{kind}{road}.png')
            )

        return panels

    def add_panel_map(self):
        if self.with_panel:
            for pic in self.panel_pics:
                self.app.game.add_widget(pic)

    def update(self):
        self._transform_sign_pic(self.pole)
        self._transform_sign_pic(self.sign)
        for pic in self.panel_pics:
            self._transform_sign_pic(pic)

    def _transform_sign_pic(self, img):
        size = self.app.lane_width * 4

        center_x = self.intersection.width / 2
        center_y = self.intersection.height / 2
        dist_from_center = self.app.lane_width*1.5
        lane = self.app.lane_width*1.5

        positions = {
            'left': [
                center_x - dist_from_center,
                center_y - lane
            ],
            'right': [
                center_x + dist_from_center,
                center_y + lane
            ],
            'behind': [
                center_x + lane,
                center_y - dist_from_center
            ],
            'ahead': [
                center_x - lane,
                center_y + dist_from_center
            ]
        }

        img.size = [size, size]
        img.center = positions[self.facing]


def _oggs_from_dir(directory):
    """List all .ogg files in a directory"""
    try:
        return [s for s in os.listdir(directory) if s.endswith('.ogg')]
    except FileNotFoundError:
        # We currently don't have any sounds for 'stop', nor a directory
        return []


class Audio:
    def __init__(self):
        # Load audio in memory (fast playback)
        self.sounds = self._get_sounds()

    def play_sound(self, sound_class):
        """
        Play a random sound of the given class
        """
        try:
            sound = random.choice(self.sounds[sound_class])
            sound.play()
        except IndexError:
            # We currently don't have any sounds for 'stop', nor a directory
            pass

    def play(self, moved: bool, correct: bool):
        """
        Play the appropriate sound, considering whether player
        is moving, and is correct in doing so
        """

        sound_class = {
            (True, True): 'drive',
            (True, False): 'crash',
            (False, True): 'stop',
            (False, False): 'honk'
        }

        self.play_sound(sound_class[(moved, correct)])

    def _get_sounds(self):
        dirs = ('drive', 'crash', 'stop', 'honk')

        choices = {}

        for d in dirs:
            choices[d] = tuple(
                SoundLoader.load(os.path.join('sounds', d, s))
                for s in _oggs_from_dir(os.path.join('sounds', d))
            )

        return choices

