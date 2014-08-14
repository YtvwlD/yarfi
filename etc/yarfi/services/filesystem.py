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
		self.description = "check filesystems and mount them"
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = True
		self.mount = None
		self.remount = None
		self.umount = None
	
	def start(self):
		Popen(["fsck", "-A", "-C"]).wait()
		self.umount = None
		self.remount = Popen(["mount", "-o", "remount,rw", "/"])
		self.mount = Popen(["mount", "-a", "--fork"])
	
	def stop(self):
		self.mount = None
		self.remount = []
		self.umount = Popen(["umount", "-a", "-r"])
	
	def status(self):
		if self.mount:
			if self.mount.poll() is not None and self.remount.poll() is not None:
				return ("running")
		elif self.umount:
			if self.umount.poll() is not None:
				if not self.remount:
					self.remount.append(Popen(["mount", "-o", "remount,rw", "/proc"]))
					self.remount.append(Popen(["mount", "-o", "remount,rw", "/sys"]))
					self.remount.append(Popen(["mount", "-o", "remount,rw", "/run"]))
					self.remount.append(Popen(["mount", "-o", "remount,rw", "/dev"]))
				else:
					finished = True
					for remount in self.remount:
						if remount.poll() is None:
							finished = False
					if finished:
						return ("stopped")
