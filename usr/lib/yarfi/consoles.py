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
from subprocess import Popen

def detect(debug):
	try:
		if Popen(["/bin/plymouth", "-ping"]).wait() == 0:
			return Plymouth(debug)
	except OSError:
		pass
	# additional checks go here (for other boot splashs)
	# ...
	# We have control over the tty!
	return Direct(debug)

class Direct:
	def __init__(self, debug):
		self.debug = debug
		try:
			os.ttyname(0)
			self.print_(2, "Direct output to tty: " + os.ttyname(0))
		except OSError as e:
			self.print_(1, str(e))
			self.print_(1, "WARNING: This is not a terminal!")
	
	def print_(self, debug, msg):
		if debug > self.debug:
			return
		if debug in [0, 1]: #err or warn
			out = sys.stderr
		else:
			out = sys.stdout
		out.write(msg)
		out.write("\n")
		out.flush()
	
	def printState(self, state):
		if not state:
			return
		clearline = "\033[K"
		with os.popen("tput cols") as tput:
			cols = int(tput.read())
		with os.popen("tput sc") as tput:
			sys.stdout.write(tput.read())
		with os.popen("tput cup 0 0") as tput:
			sys.stdout.write(tput.read())
		if isinstance(state[0][0], str):
			for status in state["targets"]:
				sys.stdout.write(clearline)
				sys.stdout.write("Targets " + status + ":")
				for target in state["targets"][status]:
					sys.stdout.write(" " + str(target))
				sys.stdout.write("\n")
			for status in state["services"]:
				sys.stdout.write(clearline)
				sys.stdout.write("Services " + status + ":")
				for service in state["services"][status]:
					sys.stdout.write(" " + str(service))
				sys.stdout.write("\n")
		else:
			sys.stdout.write(clearline)
			sys.stdout.write("Targets:")
			for target in state["targets"]:
				sys.stdout.write(" " + str(target))
			sys.stdout.write("\n")
			sys.stdout.write(clearline)
			sys.stdout.write("Services:")
			for service in state["services"]:
				sys.stdout.write(" " + str(service))
			sys.stdout.write("\n")
		sys.stdout.write(self.delimiter * (cols/2))
		self.delimiter = self.delimiter[1] + self.delimiter[0]
		sys.stdout.write("\n")
		with os.popen("tput rc") as tput:
			sys.stdout.write(tput.read())
		sys.stdout.flush()
	
	def hide(self, keep=False):
		sys.stdout.write("\n")
		if not keep:
			with os.popen("tput clear") as tput:
				sys.stdout.write(tput.read())
		sys.stdout.flush()

class Plymouth:
	def __init__(self, debug):
		self.debug = debug
	
	def print_(self, debug, msg):
		if debug > self.debug:
			return
		if debug in [0, 1]: #err or warn
			Popen(["/bin/plymouth", "report-error", msg]).wait()
		else:
			Popen(["/bin/plymouth", "display-message", "--text=" + msg]).wait()
	
	def printState(self, state):
		pass
	
	def hide(self, keep=False):
		if keep:
			Popen(["/bin/plymouth", "quit", "--retain-splash"]).wait()
		else:
			Popen(["/bin/plymouth", "quit"]).wait()
