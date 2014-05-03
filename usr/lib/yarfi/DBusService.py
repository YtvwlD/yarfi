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

from dbus import SystemBus
from dbus.service import BusName, Object, method
from dbus.mainloop.qt import DBusQtMainLoop

class DBusService(Object):
	def __init__(self):
		DBusQtMainLoop(set_as_default=True)
		self.bus = SystemBus()
		self.busName = BusName("de.ytvwld.yarfi", bus=self.bus)
		Object.__init__(self, self.busName, "/yarfi")

	@method("de.ytvwld.yarfi", in_signature="s", out_signature=None)
	def start(self, service):
		start(service)

	@method("de.ytvwld.yarfi", in_signature="s", out_signature=None)
	def stop(self, service):
		stop(service)

	@method("de.ytvwld.yarfi", in_signature="s", out_signature=None)
	def reach_target(self, target):
		reach_target(target)
