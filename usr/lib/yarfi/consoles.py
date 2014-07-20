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

class Plymouth:
	def __init__(self, debug):
		pass
