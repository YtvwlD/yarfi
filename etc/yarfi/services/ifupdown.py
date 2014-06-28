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

import subprocess
import os

class Service:
	def __init__(self):
		self.description = "Network - configured by /etc/network/interfaces"
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = False
		self.ifup = None
		self.ifdown = None
	
	def start(self):
		try:
			os.mkdir("/run/dbus/network")
		except OSError as e:
			if e.errno == 17: #the folder already exists
				pass
			else:
				raise
		self.ifup = subprocess.Popen(["ifup", "-a"])
		self.ifdown = None
	
	def stop(self):
		self.ifdown = subprocess.Popen(["ifdown", "-a"])
		self.ifup = None
		# TODO: What happens if there are mounted network filesystems?
	
	def status(self):
		if self.ifup:
			if self.ifup.returncode is not None:
				return ("running")
		elif self.ifdown:
			if self.ifdown.returncode is not None:
				return ("stopped")
