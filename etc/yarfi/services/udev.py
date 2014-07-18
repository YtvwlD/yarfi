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
from time import sleep

from yarfi.ServicesAndTargets import Service as Srv
from yarfi.ServicesAndTargets import kill

class Service(Srv):
	def __init__(self):
		self.description = "start udevd, populate /dev and load drivers"
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = True
		self.udevd = None
		self.settle = None
	
	def start(self):
		self.udevd = Popen(["/sbin/udevd"])
		sleep(5) #we can't use "--daemon" here, because we need to stop it at some point
		Popen(["/sbin/udevadm", "trigger", "--action=add"]).wait()
		self.settle = Popen(["/sbin/udevadm", "settle"])
		# TODO: Perhaps copy data from /dev/.udev to /run? (But this doesn't exist?)
		# TODO: Run udevadm monitor -e? Is this really needed?
	
	def stop(self):
		kill(self.udevd)
	
	def status(self):
		if self.udevd:
			if self.udevd.poll() is not None:
				return ("stopped")
			else:
				if self.settle.poll() is None:
					return ("running")
