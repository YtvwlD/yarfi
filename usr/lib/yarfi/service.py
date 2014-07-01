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
import os
from PySide.QtCore import QCoreApplication, QTimer
from yarfi.ServiceThread import ServiceThread

class YARFI:
	def __init__(self, debug=False):
		# a service can be: running, starting, can_start, to_start, shutting_down, to_shut_down, can_shut_down
		self.services = {}
		self.services["running"] = []
		self.services["starting"] = []
		self.services["can_start"] = []
		self.services["to_start"] = []
		self.services["shutting_down"] = []
		self.services["to_shut_down"] = []
		self.services["can_shut_down"] = []
		# a target can be: reached, to_reach
		self.targets = {}
		self.targets["reached"] = []
		self.targets["to_reach"] = []
		self.app = QCoreApplication(sys.argv)
		self.debug = debug
		self.timer = QTimer()
		self.timer.timeout.connect(self.check)
		self.delimiter = "- "

	def printDebug(self, msg):
		if self.debug:
			print (msg)
	
	def getCurrentServices(self):
		services = []
 		for status in self.services:
 			for x in self.services[status]:
 				services.append(x)
 		return (services)

	def startTimer(self):
		self.timer.setInterval(250)
		if not self.timer.isActive():
			self.timer.start()

	def check(self):
		self.printDebug("timeout - " + str(self.timer.interval()))
		self.printDebug("Checking whether targets have dependencies that have not been imported yet...")
		self.check_targets_have_dependencies()
		self.printDebug("Checking whether services have dependencies that have not been imported yet...")
		self.check_services_have_dependencies()
		self.printDebug("Checking whether a target is reached...")
		self.check_targets_are_reached()
		self.printDebug("Checking whether a service can start...")
		self.check_services_can_start()
		self.printDebug("Checking whether a service can be stopped...")
		self.check_services_can_stop()
		self.printDebug("Starting the services that can be started...")
		self.start_services()
		self.printDebug("Stopping the services that can be stopped...")
		self.stop_services()
		self.printDebug("Checking whether the status of a service has changed...")
		self.check_services_status_has_changed()
		#...
		self.printDebug("Checking if there's anything left to do...")
		if not self.targets["to_reach"] and not self.services["starting"] and not self.services["can_start"] and not self.services["to_start"] and not self.services["shutting_down"] and not self.services["to_shut_down"]:
			self.printDebug("Nothing left to do. Sleeping...")
			self.timer.stop()
		else:
			self.printDebug("Something left to do. Continuing...")
			self.timer.setInterval(self.timer.interval() * 1.25)
		self.printState()

	def check_targets_have_dependencies(self):
		"""checks whether targets have dependencies that have not been imported yet"""
		# check for targets that are missing
		for target in self.targets["to_reach"]:
			self.printDebug("Checking " + target.__module__.split(".")[1] + "...")
			remaining_dependencies = []
			for dependency in target.depends_targets:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for status in ["reached", "to_reach"]:
					for x in self.targets[status]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies.remove(dependency)
			for dependency in remaining_dependencies:
				self.printDebug("Importing " + dependency + "...")
				self.targets["to_reach"].append(__import__("targets."+dependency, fromlist=[dependency]).Target())
		# check for services that are missing
		for target in self.targets["to_reach"]:
			self.printDebug("Checking " + target.__module__.split(".")[1] + "...")
			remaining_dependencies = []
			for dependency in target.depends_services:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				services = self.getCurrentServices()
				for srv in services:
					for dependency in remaining_dependencies:
						if srv.__module__.split(".")[1] == dependency:
 							remaining_dependencies.remove(dependency)
			for dependency in remaining_dependencies:
				self.printDebug("Importing " + dependency + "...")
				self.services["to_start"].append(__import__("services."+dependency, fromlist=[dependency]).Service())

	def check_services_have_dependencies(self):
		"""checks whether services have dependencies that have not been imported yet"""
		for service in self.services["to_start"]:
			self.printDebug("Checking " + service.__module__.split(".")[1] + "...")
			remaining_dependencies = []
			for dependency in service.depends:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				services = self.getCurrentServices()
				for srv in services:
					for dependency in remaining_dependencies:
						if srv.__module__.split(".")[1] == dependency:
							remaining_dependencies.remove(dependency)
			for dependency in remaining_dependencies:
				self.printDebug("Importing " + dependency + "...")
				self.services["to_start"].append(__import__("services."+dependency, fromlist=[dependency]).Service())
	
	def check_targets_are_reached(self):
		"""checks whether a target is reached"""
		for status in self.targets:
			for target in self.targets[status]:
				self.printDebug("Checking " + target.__module__.split(".")[1] + "...")
				remaining_dependencies = {"targets": [], "services": []}
				for dependency in target.depends_targets:
					remaining_dependencies["targets"].append(dependency)
				for dependency in target.depends_services:
					remaining_dependencies["services"].append(dependency)
				for dependency in remaining_dependencies:
					for x in self.targets["reached"]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies["targets"].remove(dependency)
					for x in self.services["running"]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies["services"].remove(dependency)
				remaining_conflicts = []
				for conflict in target.conflicts:
					remaining_conflicts.append(conflict)
				for conflict in remaining_conflicts:
					isFound = False
					for status in ["running", "starting", "to_start"]:
						for x in self.services[status]:
							if x.__module__.split(".")[1] == conflict:
								isFound = True
					if not isFound:
						remaining_conflicts.remove(conflict)
				if not remaining_dependencies["targets"] and not remaining_dependencies["services"] and not remaining_conflicts:
					self.printDebug(target.__module__.split(".")[1] + " is reached.")
					if target in self.targets["to_reach"]:
						self.targets["reached"].append(target)
						self.targets["to_reach"].remove(target)
				else:
					self.printDebug(target.__module__.split(".")[1] + " is not reached.")
					if target in self.targets["reached"]:
						self.targets["reached"].remove(target) #TODO: Should it be reached again?
	
	def check_services_can_start(self):
		"""checks whether a service can start"""
		for service in self.services["to_start"]:
			self.printDebug("Checking " + service.__module__.split(".")[1] + "...")
			remaining_dependencies = []
			for dependency in service.depends:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for x in self.services["running"]:
					if x.__module__.split(".")[1] == dependency:
						remaining_dependencies.remove(dependency)
			remaining_conflicts = []
			for conflict in service.conflicts:
				remaining_conflicts.append(conflict)
			for conflict in remaining_conflicts:
				isFound = False
				for status in ["running", "starting", "to_start"]:
					for x in self.services[status]:
						if x.__module__.split(".")[1] == conflict:
							isFound = True
				if not isFound:
					remaining_conflicts.remove(conflict)
			if not remaining_dependencies and not remaining_conflicts:
				self.printDebug(service.__module__.split(".")[1] + " can start.")
				self.services["can_start"].append(service)
				self.services["to_start"].remove(service)
			else:
				self.printDebug(service.__module__.split(".")[1] + " can't start.")
				self.printDebug(" ... because there are remaining dependencies: " + str(remaining_dependencies))
				self.printDebug(" ... because there are remaining conflicts: " + str(remaining_conflicts))
	
	def check_services_can_stop(self):
		"""checks whether a service can be stopped"""
		for service in self.services["to_shut_down"]:
			self.printDebug("Checking " + service.__module__.split(".")[1] + "...")
			canBeStopped = True
			for status in ["running", "starting", "can_start", "shutting_down"]:
				for x in self.services[status]:
					if service.__module__.split(".")[1] in x.depends:
						canBeStopped = False
			if canBeStopped:
				self.printDebug(service.__module__.split(".")[1] + " can be stopped.")
				self.services["can_shut_down"].append(service)
				self.services["to_shut_down"].remove(service)
			else:
				self.printDebug(service.__module__.split(".")[1] + " can't be stopped.")

	def start_services(self):
		"""starts the services that can be started"""
		for service in self.services["can_start"]:
			self.printDebug("Starting " + service.__module__.split(".")[1] + "...")
			ServiceThread(self, service, "start").start()
			self.services["can_start"].remove(service)
			self.services["starting"].append(service)
	
	def stop_services(self):
		"""stops the services that can be stopped"""
		for service in self.services["can_shut_down"]:
			self.printDebug("Stopping " + service.__module__.split(".")[1] + "...")
			ServiceThread(self, service, "stop").start()
			self.services["can_shut_down"].remove(service)
			self.services["shutting_down"].append(service)

	def check_services_status_has_changed(self):
		"""checks whether the status of a service has changed"""
		for status in ["starting", "shutting_down"]: #TODO: check every status
			for service in self.services[status]:
				self.printDebug("Checking " + service.__module__.split(".")[1] + "...")
				ServiceThread(self, service, "status").start()
	
	def service_status_has_changed(self, service, status):
		if status in ["running", "stopped"]: #TODO: Handle crashes and respawn
			self.printDebug("The status of " + service.__module__.split(".")[1] + " has changed to '" + status + "'.")
			if service in self.services["starting"]:
				if status == "running":
					self.services["running"].append(service)
				elif status == "stopped": #Service exited during startup.
					pass #TODO: What should be done? (It will be automatically re-imported and scheduled to be started. What if there is a serious error?)
				self.services["starting"].remove(service)
			elif service in self.services["shutting_down"]:
				self.services["shutting_down"].remove(service)
	
	def printState(self):
		"""prints the current state of targets and services"""
		try:
			clearline = "\033[K"
			with os.popen("tput cols") as tput:
				cols = int(tput.read())
			with os.popen("tput sc") as tput:
				sys.stdout.write(tput.read())
			with os.popen("tput cup 0 0") as tput:
				sys.stdout.write(tput.read())
		except:
			pass
		for status in self.targets:
			sys.stdout.write(clearline)
			sys.stdout.write("Targets " + status + ":")
			for x in self.targets[status]:
				sys.stdout.write(" " + x.__module__.split(".")[1])
			sys.stdout.write("\n")
		for status in self.services:
			sys.stdout.write(clearline)
			sys.stdout.write("Services " + status + ":")
			for x in self.services[status]:
				sys.stdout.write(" " + x.__module__.split(".")[1])
			sys.stdout.write("\n")
		try:
			sys.stdout.write(self.delimiter * (cols/2))
			self.delimiter = self.delimiter[1] + self.delimiter[0]
			sys.stdout.write("\n")
			with os.popen("tput rc") as tput:
				sys.stdout.write(tput.read())
				sys.stdout.flush()
		except:
			pass

	def reach_target(self, wanted_target):
		self.printDebug ("Wanted target: " + wanted_target)
		target = __import__("targets."+wanted_target, fromlist=[wanted_target]).Target()
		self.printDebug("Trying to reach "+ target.description +" target...")
		for conflict in target.conflicts:
			for status in ["running", "starting", "to_start"]:
				for x in self.services[status]:
					if conflict == x.__module__.split(".")[1]:
						self.stop(conflict)
		for trg in target.depends_targets:
			self.reach_target(trg)
		self.targets["to_reach"].append(target)
		self.startTimer()
		self.printDebug(target.description + " target is queued to be reached.")

	def start(self, srv):
		self.printDebug ("Trying to start " + srv + "...")
		try:
			service = __import__("services."+srv, fromlist=[srv]).Service()
			self.services["to_start"].append(service)
			for conflict in service.conflicts:
				for status in ["running", "starting", "to_start"]:
					for x in self.services[status]:
						if conflict == x.__module__.split(".")[1]:
							self.stop(conflict)
			self.startTimer()
			self.printDebug (service.description + " service is queued to start.")
		except Exception as e:
			self.printDebug (srv + " could not be started. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise

	def stop(self, srv):
		self.printDebug ("Trying to stop " + srv + " service...")
		try:
			for status in self.services:
				for x in self.services[status]:
					if x.__module__.split(".")[1] == srv:
						service = x
			for status in ["running", "starting", "to_start"]:
				for x in self.services[status]:
					for dependency in x.depends:
						if dependency == service.__module__.split(".")[1]:
							self.stop(x.__module__.split(".")[1])
			self.services["to_shut_down"].append(service)
			self.startTimer()
			self.printDebug (service.description + " service is queued to be stopped.")
		except Exception as e:
			self.printDebug (service.description + " service could not be stopped. (" + str(e) + ")")
			if self.debug: #TODO: This doesn't work as expected.
				raise

	def exec_(self):
		self.app.exec_()
