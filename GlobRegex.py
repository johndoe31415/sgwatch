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
import re

class GlobRegex():
	def __init__(self, path, regex_str, predicate = None):
		self._path = os.path.realpath(os.path.expanduser(path))
		if not self._path.endswith("/"):
			self._path += "/"
		self._regex = re.compile(regex_str)
		if predicate is None:
			predicate = lambda filename: True
		self._predicate = predicate

	def __call__(self):
		for filename in os.listdir(self._path):
			full_filename = self._path + filename
			if self._predicate(full_filename):
				match = self._regex.fullmatch(filename)
				if match is not None:
					match = match.groupdict()
					yield (full_filename, match)
