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

print ("yarfi Copyright (C) 2014 Niklas Sombert")
print ("This program comes with ABSOLUTELY NO WARRANTY.")
print ("This is free software, and you are welcome to redistribute it")
print ("under certain conditions.")
print ("")

import sys
from time import sleep

if len(sys.argv) < 2:
	print ("You need to pass your selection as the first argument.")
	exit(1)

preset = sys.argv[1]

#####################presets#####################
presets = {}
presets["minimal"] = ("halt", "reboot", "poweroff", "single")
presets["multi_user"] = list(presets["minimal"])
presets["multi_user"].append("multi")
presets["multi_user"].append("multi_network")
presets["multi_user"] = tuple(presets["multi_user"])
presets["server"] = presets["multi_user"] #currently
presets["desktop"] = list(presets["multi_user"])
presets["desktop"].append("multi_x")
presets["desktop"].append("multi_x_network")
presets["desktop"] = tuple(presets["desktop"]) #more to come
#####################presets#####################

if (preset not in presets):
	print("The preset you chose ({}) isn't in the list of known presets ({}).".format(preset, presets))
	exit(1)

print ("Changing your selection to '{}'...".format(preset))
print ("Warning: This will erase some of the changes you made to yarfi's configuration!")
print ("You have 10 seconds to abort now - by hitting [CTRL]+[C]...")
try:
	sleep(10)
except KeyboardInterrupt:
	print("\nAborting...")
	exit(0)
print ("\nContinuing...")

sys.path[0] = "etc/yarfi"
sys.path.append("usr/lib")

def status(string):
	sys.stderr.write("\r\033[K" + string)
	sys.stderr.flush()

def parse_target(target, needed):
	if target in needed["targets"]:
		return #we already have done this
	status ("Parsing target '{}'...".format(target))
	needed["targets"].append(target)
	trg = __import__("targets." + target, fromlist=[target]).Target()
	for target in trg.depends_targets:
		parse_target(target, needed)
	for service in trg.depends_services:
		parse_service(service, needed)

def parse_service(service, needed):
	if service in needed["services"]:
		return #we already have done this
	status ("Parsing service '{}'...".format(service))
	needed["services"].append(service)
	srv = __import__("services." + service, fromlist=[service]).Service()
	for service in srv.depends:
		parse_service(service, needed)

needed = {}
needed["targets"] = []
needed["services"] = []

for target in presets[preset]:
	parse_target(target, needed)

status("Parsed everything.\n")
print (needed)
