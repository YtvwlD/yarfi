# YARFI - Yet Another Replacement For Init
# Copyright (C) 2014 Niklas Sombert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

class Service:
	def __init__(self):
		self.description = "execs /sbin/init"
		self.depends = []
		self.conflicts = ["dbus"]
		
	def start(self):
		os.execv("/sbin/init", sys.argv)
	
	def stop(self):
		pass
