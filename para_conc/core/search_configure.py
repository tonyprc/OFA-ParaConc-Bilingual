#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Tony Chang (42716403@qq.com)

# Disclaimer:

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum

class SearchMode(Enum):
    NORMAL = 1
    EXTENDED = 2
    REGEX = 3

class DisplayMode:
    def __init__(self):
        self.show_source = 'on'
        self.show_context = 'off'
        self.l_sent_num = 0
        self.r_sent_num = 0
        
    def set_mode(self, show_id, state):
        if show_id == "show_source":
            self.show_source = state
            return self.show_source
        if show_id == "show_context":
            self.show_context = state
            return self.show_context

class ColorMode:
    def __init__(self):
        self.ColorSet = {}
        self.ColorSet.update(self.reset_color())
        
    def set_color(self, num, color):
        if num == 1:
            self.ColorSet["HWD"] = color
        if num == 2:
            self.ColorSet["HST"] = color
        if num == 3:
            self.ColorSet["SRC"] = color

    def reset_color(self):
        self.ColorSet = {
            "HWD":"red",
            "HST":"blue",
            "SRC":"gray",}
        return self.ColorSet
        
            
class SearchRequest:
    def __init__(self):
        self.q = ''
        self.mode: SearchMode = SearchMode.EXTENDED
        self.type = ""
        self.type_value = '' 
