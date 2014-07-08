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
import time

from yarfi.ServicesAndTargets import Service as Srv

class Service(Srv):
	def __init__(self):
		self.description = "gettys on /dev/tty*"
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = True
		self.processes = []
	
	def start(self):
		for tty in range(7): #how many ttys?
			self.processes.append(subprocess.Popen(["agetty", "-8", "38400", "tty"+str(tty+1)]))
	
	def stop(self):
		for process in self.processes:
			process.terminate()
			time.sleep(5)
			if process.poll() is None:
				process.kill()
	
	def status(self):
		running = 0
		stopped = 0
		for process in self.processes:
			if process.poll() is None:
				running += 1
			else:
				stopped += 1
		if running and not stopped:
			return ("running")
		elif stopped and not running:
			return ("stopped")
