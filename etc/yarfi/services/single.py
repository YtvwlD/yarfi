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
class service:
	def __init__(self):
		self.description = "Single User Mode"
		self.depends = ["dbus"]
		self.conflicts = []
		self.respawn = True
	
	def start(self, args):
		subprocess = args["subprocess"]
		self.process = subprocess.Popen(["/sbin/sulogin"])
	
	def stop(self, args):
		self.process.terminate()
		if self.process.returncode == None:
			time.sleep(5)
			self.process.kill()
