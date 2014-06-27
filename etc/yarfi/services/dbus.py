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
import subprocess
import time

class Service:
	def __init__(self):
		self.description = "message bus"
		self.depends = ["system"]
		self.conflicts = []
		self.respawn = True
		self.process = None
	
	def start(self):
		try:
			os.mkdir("/var/run/dbus")
		except OSError as e:
			if e.errno == 17:
				pass
			else:
				raise
		passwd = open("/etc/passwd")
		for line in passwd:
			if line.startswith("messagebus"):
				uid = int(line.split(":")[2])
		passwd.close()
		group = open("/etc/group")
		for line in group:
			if line.startswith("messagebus"):
				gid = int(line.split(":")[2])
		group.close()
		os.chown("/var/run/dbus", uid, gid)
		subprocess.Popen(["dbus-uuidgen", "--ensure"]).wait()
		self.process = subprocess.Popen(["dbus-daemon", "--system"])
	
	def stop(self):
		self.process.terminate()
		if self.process.returncode is None:
			time.sleep(5)
			self.process.kill()
		os.remove("/var/run/dbus/pid")
	
	def status(self):
		if self.process:
			if self.process.returncode is None:
				test = subprocess.Popen(["python", "/etc/yarfi/services/dbus.py"])
				test.wait()
				if test.returncode == 0:
					return ("running")
			else:
				return ("stopped")

if __name__ == "__main__":
	import sys
	sys.path.remove(sys.path[0])
	
	from dbus import SystemBus
	from dbus.exceptions import DBusException
	
	try:
		SystemBus()
		sys.exit(0)
	except DBusException:
		sys.exit(1)
