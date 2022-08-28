#! /usr/bin/python
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

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.config import Config

import random
from time import time
from model import PlayerCar, Car, Sign, Audio
from math import ceil


def choice(collection):
    """Like random.choice, but works on sets"""
    return random.choice(list(collection))


class Intersection:
    def __init__(self, app, game):
        self.app = app
        self.game = game

        self.roads = []  # Roads of NPCs
        self.other_cars = []
        self.type = 'controlled'
        self.time = time()
        self.touch_start_y = False
        self.player_move = None
        self.last_frame_touch_y = None  # Used for animating car while choosing direction
        self.player_seen_output = False
        self.label = Label(text='', outline_color = [0,0,0,.7])
        self.correct = None # Player moved correctly

    @property
    def width(self):
        return self.game.width

    @property
    def height(self):
        return self.game.height

    def start(self):
        self.init_roads()
        self.init_cars()
        self.init_signs()

    def on_touch_down(self, touch):
        if not self.touch_start_y:
            self.touch_start_y = touch.y
            self.last_frame_touch_y = touch.y

    def on_touch_up(self, touch):
        if touch.y < self.height* 0.8:
            # User is not trying to access the status bar

            if self.touch_start_y and not self.player_move:
                # Short move finalized
                self.label.text = 'You are the red car.\nSwipe up to go, or down to stop!'
                self.label.color = [1, 1, 0, 1]
                self.touch_start_y = None

            elif self.player_move and self.player_seen_output:
                # Second time we touch down: we want a new scene
                if self.correct is None:
                    raise ValueError('Correct is None')
                self.game.next_turn(self.correct)
            else:
                # Long move just finalized
                self.player_seen_output = True

    def on_touch_move(self, touch):
        if self.touch_start_y and not self.player_move:
            self.player.center_y += touch.y-self.last_frame_touch_y
            self.last_frame_touch_y = touch.y

        if touch.y - self.app.lane_width/2 > self.touch_start_y:
            self.player_move = 'go'
            self.moved()
        elif touch.y + self.app.lane_width/2 < self.touch_start_y:
            self.player_move = 'stop'
            self.moved()

    def moved(self):
        correct = ((self.player_move == 'stop') == (self.player.must_yield))

        # If you want an example of violating the Law of Demeter, here it is:
        self.app.audio.play(self.player_move == 'go', correct)

        if correct:
            self.label.color = [.3, 1, .3, 1]
            action = 'stopped' if self.player_move == 'stop' else 'went'
            self.label.text = f'Correct!\nYou {action}.\nScore so far: {self.game.score+1}'
        else:
            self.label.color = [1, .3, .3, 1]
            self.label.text = f'You lost!\n{self.player.reason}\nScore: {self.game.score}'

        self.correct = correct

    def update(self, _):
        self.app.lane_width = self.width * 0.2
        if not self.touch_start_y:
            self.player.center_x = self.width/2 + self.app.lane_width/2
        self.update_cars()
        self.update_roads()
        self.update_signs()
        self.update_label()

    def update_cars(self):
        self.player.update()
        for car in self.other_cars:
            car.update()

    def update_roads(self):
        road_coords ={
            'left': {
                'x': 0,
                'y': self.height / 2 - self.app.lane_width,
                'w': self.width/2 + self.app.lane_width,
                'h': self.app.lane_width * 2
            },
            'ahead': {
                'x': self.width/2 - self.app.lane_width,
                'y': self.height / 2,
                'w': self.app.lane_width * 2,
                'h': self.height - self.height / 2,
            },
            'right': {
                'x': self.width/2 - self.app.lane_width,
                'y': self.height / 2 - self.app.lane_width,
                'w': self.width/2 + self.app.lane_width,
                'h': self.app.lane_width * 2
            },
            'behind': {
                'x': self.width/2 - self.app.lane_width,
                'y': 0,
                'w': self.app.lane_width * 2,
                'h': self.height / 2,
            },
        }

        for rn in self.roads:
            road = self.roads[rn]
            road.pos = [
                road_coords[rn]['x'],
                road_coords[rn]['y'],
            ]
            road.size = [
                road_coords[rn]['w'],
                road_coords[rn]['h'],

            ]

    def update_signs(self):
        for sign in self.signs:
            sign.update()

    def update_label(self):
        self.label.center_x = self.width/2
        self.label.center_y = self.height/3
        self.label.text_size = [self.width*.8, self.height/5]
        self.label.font_size = ceil(self.width * 0.04)
        self.label.outline_width = ceil(self.width * 0.005)

    def init_roads(self):
        num_roads = random.choice([3, 4])

        road_names = ['left', 'ahead', 'right']
        if num_roads != 4:
            assert num_roads == 3
            del road_names[random.choice([0, 1, 2])]

        # We want yield-only and controlled intersections more often
        self.type = random.choices(
            ['uncontrolled', 'yield-sign-only', 'controlled'],
            weights=[1, 2, 3]
        )[0]

        self.roads = {}
        with self.game.canvas:
            Color(.25, .25, .25)
            for rn in road_names:
                self.roads[rn] = Rectangle()

            # Mandatory road where player comes from
            self.roads['behind'] = Rectangle()

        self._generate_road_prios()

    def _generate_road_prios(self):
        self.prios = {road: False for road in self.roads}

        if self.type == 'uncontrolled':
            chosen_prios = []
        elif self.type == 'yield-sign-only':
            # We can only choose between opposite roads to have priority
            opposites = [{'behind', 'ahead'}, {'left', 'right'}]
            possible_prio_pair = []
            for pair in opposites:
                if len(pair.intersection(self.roads.keys())) == 2:
                    # Both roads in pair exist
                    possible_prio_pair.append(pair)
            chosen_prios = random.choice(possible_prio_pair)
        elif self.type == 'controlled':
            chosen_prios = random.sample(self.roads.keys(), 2)

        for road in chosen_prios:
            self.prios[road] = True

    def init_cars(self):
        # Player
        self.player = PlayerCar(
            source_road='behind',
            target_road=choice(set(self.roads.keys()) - {'behind'}),
            app=self.app
        )
        self.game.add_widget(self.player)

        # Other cars
        self.other_cars = []
        for road_n in set(self.roads) - {'behind'}:
            if random.random() < 2:
                target_road = choice(set(self.roads.keys()) - {road_n})
                self.other_cars.append(
                    Car(
                        source_road=road_n,
                        target_road=target_road,
                        app=self.app
                    )
                )
        for car in self.other_cars:
            self.game.add_widget(car)

        for car in [self.player] + self.other_cars:
            car.must_yield, car.reason = \
                car.must_yield(self.other_cars, self.prios)

    def init_signs(self):
        self.signs = []
        if self.type != 'uncontrolled':
            for road in self.roads:
                if self.type == 'controlled' and self.prios[road]:
                    self.signs.append(Sign(self.app, 'prio', road, True))
                elif self.type == 'controlled' and not self.prios[road]:
                    self.signs.append(Sign(self.app, 'yield', road, True))
                elif not self.prios[road]:
                    # No minimap panel
                    self.signs.append(Sign(self.app, 'yield', road, False))

        self.game.add_widget(self.label)


class YieldOrDieGame(Widget):
    """Remember score and rebuild intersection each turn"""
    def __init__(self, app):
        Widget.__init__(self)
        self.score = 0
        self.app = app
        self.intersection = Intersection(self.app, self)

    def start(self):
        self.intersection.start()

    def on_touch_down(self, touch):
        self.intersection.on_touch_down(touch)
    def on_touch_up(self, touch):
        self.intersection.on_touch_up(touch)
    def on_touch_move(self, touch):
        self.intersection.on_touch_move(touch)

    def next_turn(self, won):
        if won:
            self.score += 1
        else:
            self.score = 0
        self.canvas.clear()
        self.intersection = Intersection(self.app, self)
        self.start()
        self.intersection.update(0)

    def update(self, seconds_since_last_update):
        self.intersection.update(seconds_since_last_update)

class YieldOrDieApp(App):
    lane_width = NumericProperty(1)
    intersection_center_height = 0

    def build(self):
        self.game = YieldOrDieGame(app=self)
        self.audio = Audio()
        Clock.schedule_interval(self.game.update, 1.0/40.0)

        return self.game

    def on_start(self):
        self.game.start()


if __name__ == '__main__':
    # import doctest; doctest.testmod()
    k=60

    Config.set('graphics', 'width',  9*k)
    Config.set('graphics', 'height', 16*k)
    YieldOrDieApp().run()
