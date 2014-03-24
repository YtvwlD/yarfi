#!/usr/bin/env python

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
import sys
import subprocess
import dbus
import dbus.service
import time

def reach_target(target):
	os.chdir("/etc/yarfi/targets")
	Target = __import__(wanted_target).target()
	for conflict in Target.conflicts:
		for srv in services:
			if conflict == srv.__name__:
				stop(conflict)
	remaining_dependencies = Target.depends
	for srv in services:
		for dependency in remaining_dependencies:
			if srv.__name__ == dependency:
				remaining_dependencies.remove(dependency)
	for dependency in remaining_dependencies:
		start(dependency)

def start(srv):
	os.chdir("/etc/yarfi/services")
	Service = __import__(srv).service()
	for conflict in Service.conflicts:
		for x in services:
			if conflict == x.__name__:
				stop(conflict)
	remaining_dependencies = Service.depends
	for x in services:
		for dependency in remaining_dependencies:
			if x.__name__ == dependency:
				remaining_dependencies.remove(dependency)
	for dependency in remaining_dependencies:
		start(dependency)
	Service.start(args)
	services.append(Service)
	
def stop(srv):
	for x in services:
		if x.__name__ == srv:
			Service = x
	for x in services:
		for dependency in x.depends:
			if dependency == x.__name__:
				stop(dependency)
	Service.stop(args)
	services.remove(Service)

args = {"os": os, "sys": sys, "subprocess": subprocess, "time": time}

services = []

wanted_target = ""
cmdline = open("/proc/cmdline")
for line in cmdline:
	params = line.split(" ")
	for x in params:
		z = x.split("=")
		if z[0] == "yarfi-target":
			wanted_target = z[1]
cmdline.close()
if wanted_target == "":
	wanted_target = "default"

class DBusService(dbus.service.Object):
	def __init__(self):
		busName = dbus.service.BusName("yarfi", bus=dbus.SystemBus())
		dbus.service.Object.__init__(self, busName, "/yarfi")
	
	@dbus.service.method("yarfi.start", in_signature="s", out_signature=None)
	def start(self, service):
		start(service)
	
	@dbus.service.method("yarfi.stop", in_signature="s", out_signature=None)
	def stop(self, service):
		stop(service)
	
	@dbus.service.method("yarfi.reach_target", in_signature="s", out_signature=None)
	def reach_target(self, target):
		reach_target(target)

reach_target(wanted_target)
