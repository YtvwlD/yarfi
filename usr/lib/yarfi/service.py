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
		# a service can be: running, starting, can_start, to_start, shutting_down, to_shut_down
		self.services = {}
		self.services["running"] = []
		self.services["starting"] = []
		self.services["can_start"] = []
		self.services["to_start"] = []
		self.services["shutting_down"] = []
		self.services["to_shut_down"] = []
		# a target can be: reached, to_reach
		self.targets = {}
		self.targets["reached"] = []
		self.targets["to_reach"] = []
		self.app = QCoreApplication(sys.argv)
		self.debug = debug
		self.timer = QTimer()
		self.timer.timeout.connect(self.check)
		self.timer.setInterval(250)
		self.timer.start()

	def check(self):
		self.check_targets_have_dependencies()
		self.check_services_have_dependencies()
		self.check_targets_have_all_dependencies_met()
		self.check_services_have_all_dependencies_met()
		self.start_services()
		#...
		self.printState()
		self.timer.setInterval(self.timer.interval() * 1.25)

	def check_targets_have_dependencies(self):
		"""checks whether targets have dependencies that have not been imported yet"""
		# check for targets that are missing
		for target in self.targets_needed:
			remaining_dependencies = []
			for dependency in target.depends_targets:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for status in ["reached", "to_reach"]:
					for x in self.targets[status]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies.remove(dependency)
			for dependency in remaining_dependencies:
				self.targets_needed.append(__import__("targets."+dependency, fromlist=[dependency]).Target())
		# check for services that are missing
		for target in self.targets["to_reach"]:
			remaining_dependencies = []
			for dependency in target.depends_services:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for status in ["running", "starting", "to_start"]:
					for x in self.services[status]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies.remove(dependency)
				for dependency in remaining_dependencies:
					self.services["to_start"].append(__import__("services."+dependency, fromlist=[dependency]).Service())

	def check_services_have_dependencies(self):
		"""checks whether services have dependencies that have not been imported yet"""
		for service in self.services["to_start"]:
			remaining_dependencies = []
			for dependency in service.depends:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for status in ["running", "starting", "to_start"]:
					for x in self.services[status]:
						if x.__module__.split(".")[1] == dependency:
							remaining_dependencies.remove(dependency)
				for dependency in remaining_dependencies:
					self.services["to_start"].append(__import__("services."+dependency, fromlist=[dependency]).Service())
	
	def check_targets_have_all_dependencies_met(self):
		"""checks whether all dependencies of a target are met"""
		for target in self.targets["to_reach"]:
			remaining_dependencies = []
			for dependency in target.depends_targets:
				remaining_dependencies.append(dependency)
			for dependency in target.depends_services:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for x in self.targets["reached"]:
					if x.__module__.split(".")[1] == dependency:
						remaining_dependencies.remove(dependency)
				for x in self.services["running"]:
					if x.__module__.split(".")[1] == dependency:
						remaining_dependencies.remove(dependency)
			if not remaining_dependencies:
				self.targets_reached.append(target)
				self.targets_needed.remove(target)
	
	def check_services_have_all_dependencies_met(self):
		"""checks whether all dependencies of a service are met"""
		for service in self.services["to_start"]:
			remaining_dependencies = []
			for dependency in service.depends:
				remaining_dependencies.append(dependency)
			for dependency in remaining_dependencies:
				for x in self.services["running"]:
					if x.__module__.split(".")[1] == dependency:
						remaining_dependencies.remove(dependency)
			if not remaining_dependencies:
				self.services["can_start"].append(service)
				self.services["to_start"].remove(service)
	
	def start_services(self):
		"""starts the services that can be started"""
		for service in self.services["can_start"]:
			ServiceThread(service, "start").start()
	
	def printState(self):
		"""prints the current state of targets and services"""
		clearline = "\033[K"
		with os.popen("tput cols") as tput:
			cols = int(tput.read())
		with os.popen("tput sc") as tput:
			sys.stdout.write(tput.read())
		with os.popen("tput cup 0 0") as tput:
			sys.stdout.write(tput.read())
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
			sys.stdout.write("-" * cols)
			sys.stdout.write("\n")
		with os.popen("tput rc") as tput:
			sys.stdout.write(tput.read())
			sys.stdout.flush()

	def reach_target(self, wanted_target):
		if self.debug:
			print ("Wanted target: " + wanted_target)
		target = __import__("targets."+wanted_target, fromlist=[wanted_target]).Target()
		print("Trying to reach "+ target.description +" target...")
		for conflict in target.conflicts:
			for srv in self.services:
				if conflict == srv.__module__.split(".")[1]:
					self.stop(conflict)
		for trg in target.depends_targets:
			self.reach_target(trg)
		remaining_dependencies = target.depends_services
		for srv in self.services:
			for dependency in remaining_dependencies:
				if srv.__module__.split(".")[1] == dependency:
					remaining_dependencies.remove(dependency)
		for dependency in remaining_dependencies:
			self.start(dependency)
		print(target.description + " target reached.")

	def start(self, srv):
		print ("Trying to start " + srv + "...")
		try:
			service = __import__("services."+srv, fromlist=[srv]).Service()
			self.services["to_start"].append(service)
			for conflict in service.conflicts:
				for status in ["running", "starting", "to_start"]:
					for x in self.services[status]:
						if conflict == x.__module__.split(".")[1]:
							self.stop(conflict)
			print (service.description + " service is queued to start.")
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
