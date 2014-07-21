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
		self.description = "reboots the system"
		self.depends = []
		self.conflicts = ["system", "single"] # do NOT invoke this directly! (use the "reboot" target instead)
		self.process = None
	
	def start(self):
		self.process = Popen(["/sbin/reboot", "-f"])
	
	def stop(self):
		pass
	
	def status(self):
		if self.process:
			if self.process.poll() is not None:
				return ("running")
