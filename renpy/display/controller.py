# Copyright 2004-2015 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pygame_sdl2.controller
import renpy.display

from pygame_sdl2 import CONTROLLERDEVICEADDED, CONTROLLERDEVICEREMOVED
from pygame_sdl2 import CONTROLLERAXISMOTION, CONTROLLERBUTTONDOWN, CONTROLLERBUTTONUP
from pygame_sdl2.controller import Controller, get_string_for_axis, get_string_for_button

def init():
    """
    Initialize gamepad support.
    """

    if not renpy.game.preferences.pad_enabled:
        return

    pygame_sdl2.controller.init()

# A map from controller index to controller object.
controllers = { }

# A map from (controller, axis) to "pos", "neg", None position.
axis_positions = {}

# The axis threshold.
THRESHOLD = (32768 // 2)

def make_event(name):
    """
    Creates an EVENTNAME event with `name`, and returns it.
    """

    names = [ name ]

    names.extend(renpy.config.pad_bindings.get(name, ()))

    return pygame_sdl2.event.Event(
        renpy.display.core.EVENTNAME,
        { "eventnames" : names, "controller" : name, "up" : False })


def event(ev):
    """
    Processes an event and returns the same event, a new event, or None if
    the event has been processed and should be ignored.
    """

    if ev.type == CONTROLLERDEVICEADDED:
        if ev.which not in controllers:
            controllers[ev.which] = c = Controller(ev.which)
            c.init()

        return None

    elif ev.type == CONTROLLERDEVICEREMOVED:

        if ev.which in controllers:
            c = controllers.pop(ev.which)
            c.quit()

        return None

    elif ev.type == CONTROLLERAXISMOTION:

        if ev.value > THRESHOLD:
            pos = "pos"
        elif ev.value < -THRESHOLD:
            pos = "neg"
        else:
            pos = None

        old_pos = axis_positions.get((ev.which, ev.axis), None)

        if pos == old_pos:
            return None

        axis_positions[(ev.which, ev.axis)] = pos

        if pos is None:
            return None

        name = "pad_{}_{}".format(get_string_for_axis(ev.axis), pos)
        ev = make_event(name)

    elif ev.type in (CONTROLLERBUTTONDOWN, CONTROLLERBUTTONUP):

        if ev.type == CONTROLLERBUTTONDOWN:
            pr = "press"
        else:
            pr = "release"

        name = "pad_{}_{}".format(get_string_for_button(ev.button), pr)
        ev = make_event(name)

    return ev
