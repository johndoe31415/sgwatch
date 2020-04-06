#!/usr/bin/python3
#	sgwatch - Watch savegames and create backups
#	Copyright (C) 2019-2020 Johannes Bauer
#
#	This file is part of sgwatch.
#
#	sgwatch is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	sgwatch is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with sgwatch; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import hashlib
import struct
import io
import collections
import tarfile
import time
import datetime
import json

class Savefile():
	_QuickStruct = struct.Struct("< Q")

	def __init__(self, filename, mandatory = True):
		self._filename = os.path.realpath(os.path.expanduser(filename))
		self._mandatory = mandatory

	@property
	def satisfied(self):
		return (not self._mandatory) or os.path.isfile(self._filename)

	@property
	def mtime(self):
		if os.path.isfile(self._filename):
			return os.stat(self._filename).st_mtime
		else:
			return 0

	def quickhash(self):
		if not os.path.isfile(self._filename):
			return bytes(16)
		else:
			stat_result = os.stat(self._filename)
			serialized = self._QuickStruct.pack(int(stat_result.st_mtime * 1000))
			return hashlib.md5(serialized).digest()

	def slowhash(self):
		md5 = hashlib.md5()
		with open(self._filename, "rb") as f:
			while True:
				chunk = f.read(1024 * 1024)
				if len(chunk) == 0:
					break
				md5.update(chunk)
		return md5.digest()

	def store(self, archive, pathname):
		info = archive.gettarinfo(self._filename, arcname = pathname)
		with open(self._filename, "rb") as f:
			archive.addfile(info, fileobj = f)
		return [{
			"src":		self._filename,
			"dst":		pathname,
			"mtime":	os.stat(self._filename).st_mtime,
		}]

	def to_json(self):
		return {
			"type":			"file",
			"file":			self._filename,
			"mandatory":	self._mandatory,
		}

	def __repr__(self):
		return "Savefile<%s>" % (self._filename)

class Savedir():
	def __init__(self, pathname, mandatory = True):
		self._pathname = os.path.realpath(os.path.expanduser(pathname))
		if not self._pathname.endswith("/"):
			self._pathname += "/"
		self._mandatory = mandatory

	@property
	def satisfied(self):
		return (not self._mandatory) or os.path.isdir(self._pathname)

	@property
	def mtime(self):
		maxmtime = 0
		for filename in self.filelist:
			mtime = os.stat(filename).st_mtime
			maxmtime = max(mtime, maxmtime)
		return maxmtime

	@property
	def filelist(self):
		if not os.path.isdir(self._pathname):
			return
		filelist = [ ]
		for (path, subdirs, files) in os.walk(self._pathname):
			if not path.endswith("/"):
				path += "/"
			for filename in files:
				filelist.append(path + filename)
		filelist.sort()
		return filelist

	def _chainhash(self, component_function):
		md5 = hashlib.md5()
		for filename in self.filelist:
			md5.update(component_function(Savefile(filename)))
		return md5.digest()

	def quickhash(self):
		return self._chainhash(lambda savefile: savefile.quickhash())

	def slowhash(self):
		return self._chainhash(lambda savefile: savefile.slowhash())

	def store(self, archive, pathname):
		result = [ ]
		for filename in self.filelist:
			rel_filename = filename[len(self._pathname):]
			arc_filename = pathname + "/" + rel_filename
			info = archive.gettarinfo(filename, arcname = arc_filename)
			with open(filename, "rb") as f:
				archive.addfile(info, fileobj = f)
			result.append({
				"src":		filename,
				"dst":		arc_filename,
				"mtime":	os.stat(filename).st_mtime,
			})
		return result

	def to_json(self):
		return {
			"type":			"dir",
			"path":			self._pathname,
			"mandatory":	self._mandatory,
		}

class Savegame():
	_Component = collections.namedtuple("Component", [ "component", "shortcut" ])
	def __init__(self):
		self._components = [ ]

	@property
	def satisfied(self):
		return all(component.component.satisfied for component in self._components)

	@property
	def mtime(self):
		return max(component.component.mtime for component in self._components)

	@classmethod
	def new_component(cls, pathname, mandatory = True):
		if os.path.isdir(pathname):
			return Savedir(pathname, mandatory = mandatory)
		else:
			return Savefile(pathname, mandatory = mandatory)

	def add(self, component, shortcut = None):
		if shortcut is None:
			shortcut = "component-%02d" % (len(self._components))
		self._components.append(self._Component(component = component, shortcut = shortcut))

	def _chainhash(self, component_function):
		md5 = hashlib.md5()
		for component in self._components:
			md5.update(component_function(component.component))
		return md5.digest()

	def quickhash(self):
		return self._chainhash(lambda component: component.quickhash())

	def slowhash(self):
		return self._chainhash(lambda component: component.slowhash())

	def store(self, filename):
		quickhash = self.quickhash()
		slowhash = self.slowhash()
		with tarfile.open(filename, "w:gz") as archive:
			stored = [ ]
			for component in self._components:
				stored += component.component.store(archive, "sgwatch-data/content/" + component.shortcut)

			metadata = {
				"quickhash":	quickhash.hex(),
				"slowhash":		slowhash.hex(),
				"components":	[ component.component.to_json() for component in self._components ],
				"timestamp":	datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
				"stored":		stored,
			}
			metadata_json = (json.dumps(metadata) + "\n").encode()

			info = archive.tarinfo(name = "sgwatch-data/metadata.json")
			info.size = len(metadata_json)
			info.mtime = time.time()
			with io.BytesIO(metadata_json) as metadata_f:
				archive.addfile(info, fileobj = metadata_f)

	def __repr__(self):
		return "Savegame<%s>" % (", ".join(str(component) for component in self._components))

if __name__ == "__main__":
	#x = Savedir("/usr/lib/firefox")
	x = Savefile("/bin/bash")
	print(x.quickhash())
	print(x.slowhash())

	sg = Savegame()
	sg.add(x)
	sg.store("image.tar.gz")
