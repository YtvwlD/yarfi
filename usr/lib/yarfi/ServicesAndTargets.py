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

class ServicesAndTargets:
	def __str__(self):
		return (self.__module__.split(".")[1])

class Service(ServicesAndTargets):
	def __init__(self): #At least copy and modify this.
		self.description = "No description here."
		self.depends = []
		self.conflicts = []
		self.status_ = ""
	
	def start(self):
		self.status_ = "running"
	
	def stop(self):
		self.status_ = "stopped"
	
	def status(self):
		return (self.status_)

class Target(ServicesAndTargets):
	pass
