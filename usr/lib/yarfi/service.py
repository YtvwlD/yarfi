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

import sys
from PySide.QtCore import QCoreApplication

class YARFI:
	def __init__(self, debug=False):
		self.services = []
		self.app = QCoreApplication(sys.argv)
		self.debug = debug

	def reach_target(self, wanted_target):
		if self.debug:
			print ("Wanted target: " + wanted_target)
		target = __import__("targets."+wanted_target, fromlist=[wanted_target]).Target()
		print("Trying to reach "+ target.description +" target...")
		for conflict in target.conflicts:
			for srv in self.services:
				if conflict == srv.__name__:
					self.stop(conflict)
		for trg in target.depends_targets:
			self.reach_target(trg)
		remaining_dependencies = target.depends_services
		for srv in self.services:
			for dependency in remaining_dependencies:
				if srv.__name__ == dependency:
					remaining_dependencies.remove(dependency)
		for dependency in remaining_dependencies:
			self.start(dependency)
		print(target.description + " target reached.")

	def start(self, srv):
		print ("Trying to start " + srv + "...")
		try:
			service = __import__("services."+srv, fromlist=[srv]).Service()
			for conflict in service.conflicts:
				for x in self.services:
					if conflict == x.__module__.split(".")[1]:
						self.stop(conflict)
			remaining_dependencies = service.depends
			for x in self.services:
				for dependency in remaining_dependencies:
					if x.__module__.split(".")[1] == dependency:
						remaining_dependencies.remove(dependency)
			for dependency in remaining_dependencies:
				self.start(dependency)
			service.start()
			self.services.append(service)
			print (service.description + " service was started successfully.")
		except Exception as e:
			print (srv + " could not be started. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise

	def stop(self, srv):
		print ("Trying to stop " + srv + " service...")
		try:
			for x in self.services:
				if x.__module__.split(".")[1] == srv:
					service = x
			for x in self.services:
				for dependency in x.depends:
					if dependency == x.__module__.split(".")[1]:
						self.stop(dependency)
			service.stop()
			self.services.remove(service)
			print (service.description + " service was stopped successfully.")
		except Exception as e:
			print (service.description + " service could not be stopped. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise

	def exec_(self):
		self.app.exec_()
