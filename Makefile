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

all:
	echo "Compiling an interpreted language is difficult."
	echo "If you really want to do that run 'compile-pyc' or 'compile-pyx'."

compile-pyc:
	echo "You need to run either 'compile-pyc-2' (for Python 2) or 'compile-pyc-3' (for Python 3)."

compile-pyc-2:
	pycompile .

compile-pyc-3:
	py3compile .

compile-pyx:
	echo "You need to run either 'compile-pyx-2' (for Python 2.7) or 'compile-pyx-3' (for Python 3.4) or 'compile-pyx32' (for Python 3.2)."

compile-pyx-2:
# This may probably not work.
	find | grep [.]py | grep -v [.]pyc | xargs cython -2
	find * | grep [.]c | grep -v [.]conf | cut -d. -f1 | xargs -I x gcc -Wall -fPIC -pthread -O2 -shared -I/usr/include/python2.7 -o x.so x.c

compile-pyx-3:
# This may probably not work.
	find | grep [.]py | grep -v [.]pyc | xargs cython -3
	find * | grep [.]c | grep -v [.]conf | cut -d. -f1 | xargs -I x gcc -Wall -fPIC -pthread -O2 -shared -I/usr/include/python3.4 -o x.so x.c

compile-pyx-32:
# This may probably not work.
	find | grep [.]py | grep -v [.]pyc | xargs cython -3
	find * | grep [.]c | grep -v [.]conf | cut -d. -f1 | xargs -I x gcc -Wall -fPIC -pthread -O2 -shared -I/usr/include/python3.2mu -o x.so x.c

clean:
	find | grep [.]pyc | xargs -I x rm -f x
	find | grep [.]c | grep -v [.]conf | xargs -I x rm -f x
	find | grep [.]so | xargs -I x rm -f x

install:
	cp -R usr/* /usr/
	cp -R etc/* /etc/
	cp sbin/* /sbin/

remove:
	echo "Removing all files from / that exist in this directory..."
	echo "If you have run 'make clean' before, you have to compile again."
	find * | grep -v [.]git | grep / | xargs -I x rm -df /x 2>/dev/null || true
	find * | grep -v [.]git | grep / | xargs -I x rmdir -p --ignore-fail-on-non-empty /x 2>/dev/null || true
