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

from subprocess import Popen

from yarfi.ServicesAndTargets import Service as Srv

class Service(Srv):
	def __init__(self):
		self.description = "set the console font and keyboard layout"
		self.depends = []
		self.conflicts = []
		self.status_ = ""
		self.process = None
	
	def start(self):
		self.process = Popen(["/bin/setupcon"]) #use --force? (and --save?)
	
	def status(self):
		if self.status_ == "stopped":
			return ("stopped")
		if self.process:
			if self.process.poll() is not None:
				self.status_ = "running"
				return ("running")
