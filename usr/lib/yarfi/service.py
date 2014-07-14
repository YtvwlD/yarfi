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
from PySide.QtCore import QCoreApplication, QTimer

class YARFI:
	def __init__(self, debug=False):
		self.services = []
		self.app = QCoreApplication(sys.argv)
		self.debug = debug
		self.respawnTimer = QTimer()
		self.respawnTimer.timeout.connect(self.respawn)
		self.respawnTimer.setInterval(30000) #is 30 seconds the right interval?
		self.respawnTimer.start()

	def reach_target(self, wanted_target):
		if self.debug:
			print ("Wanted target: " + wanted_target)
		target = __import__("targets."+wanted_target, fromlist=[wanted_target]).Target()
		print("Trying to reach "+ target.description +" target...")
		for srv in self.services:
			if str(srv) in target.conflicts:
				self.stop(str(srv))
		for trg in target.depends_targets:
			self.reach_target(trg)
		remaining_dependencies = target.depends_services[:]
		for srv in self.services:
			if str(srv) in remaining_dependencies:
				remaining_dependencies.remove(str(srv))
		for dependency in remaining_dependencies:
			self.start(dependency)
		print(target.description + " target reached.")
		sys.stdout.write("Eliminating zombie processes...")
		sys.stdout.flush()
		for service in self.services:
			# TODO: If the service has died, this will return "stopped". What to do then?
			service.status()
		sys.stdout.write(" ...done.\n")
		sys.stdout.flush()

	def start(self, srv):
		print ("Trying to start " + srv + "...")
		try:
			service = __import__("services."+srv, fromlist=[srv]).Service()
			for srv in self.services:
				if str(srv) in service.conflicts:
					self.stop(str(srv))
			remaining_dependencies = service.depends[:]
			for srv in self.services:
				if str(srv) in remaining_dependencies:
					remaining_dependencies.remove(str(srv))
			for dependency in remaining_dependencies:
				self.start(dependency)
			service.start()
			self.services.append(service)
			print (service.description + " service was started successfully.")
		except Exception as e:
			print (str(srv) + " could not be started. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise

	def stop(self, srv):
		print ("Trying to stop " + srv + " service...")
		try:
			for x in self.services:
				if str(x) == srv:
					service = x
			for x in self.services:
				if str(service) in x.depends:
					self.stop(str(x))
			service.stop()
			self.services.remove(service)
			print (service.description + " service was stopped successfully.")
		except Exception as e:
			print (service.description + " service could not be stopped. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise
	
	def respawn(self):
		if self.debug:
			print ("Checking whether a service has exited...")
		for service in self.services[:]:
			if service.status() == "stopped":
				print (service.description + " service has exited.")
				if service.respawn:
					print ("Respawning it..")
					service.start()
				else:
					print ("Removing it from the list of running services...")
					self.services.remove(service)
	
	def exec_(self):
		self.app.exec_()
