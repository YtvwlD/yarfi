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

from yarfi.ServicesAndTargets import Service as Srv

class Service(Srv):
	def __init__(self):
		self.description = "mount filesystems" #and check them?
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = True
		self.mount = None
		self.remount = None
		self.umount = None
	
	def start(self):
		# TODO: Check the filesystems if they need to be checked.
		self.umount = None
		self.remount = subprocess.Popen(["mount", "-o", "remount,rw", "/"])
		self.mount = subprocess.Popen(["mount", "-a", "--fork"])
	
	def stop(self):
		self.mount = None
		self.remount = None
		self.umount = subprocess.Popen(["umount", "-a", "-r"])
	
	def status(self):
		if self.mount:
			if self.mount.poll() is not None and self.remount.poll() is not None:
				return ("running")
		elif self.umount:
			if self.umount.poll() is not None:
				return ("stopped")
