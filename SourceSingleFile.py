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
from GlobRegex import GlobRegex
from Savegame import Savegame, Savefile

class SourceSingleFile():
	def __init__(self, source_definition):
		self._source_glob = GlobRegex(source_definition["source"][0], source_definition["source"][1], predicate = os.path.isfile)
		self._restore_filename = source_definition["restore"]

	def find(self):
		for (filename, variables) in self._source_glob():
			savegame = Savegame()
			savegame.add(Savegame.new_component(filename), shortcut = "savefile.bin")
			yield savegame

	def restore(self, savegame):
		content = savegame.get_file("savefile.bin")
		with open(self._restore_filename, "wb") as f:
			f.write(content)

if __name__ == "__main__":
	src = SourceSingleFile({ "source": [ ".", ".*\.py" ], "restore": "/tmp/restored.bin" })
	for savegame in src.find():
		print(savegame, savegame.quickhash())
