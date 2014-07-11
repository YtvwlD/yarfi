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

from threading import Thread

class ServiceThread(Thread):
	def __init__(self, yarfi, service, action):
		Thread.__init__(self)
		self.service = service
		self.action = action
		self.yarfi = yarfi
	
	def run(self):
		if self.action == "status":
			status = self.service.status()
			if status == "running":
				self.yarfi.service_status_has_changed(self.service, status)
			if status == "stopped":
				self.yarfi.service_status_has_changed(self.service, status)
		else:
			exec("self.service."+self.action+"()")