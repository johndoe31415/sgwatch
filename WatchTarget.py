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

class WatchTarget():
	_TARGET_TYPES = { }
	_TARGET_NAME = None

	@classmethod
	def register(cls, target_class):
		name = target_class._TARGET_NAME
		if name in cls._TARGET_TYPES:
			raise Exception("Multiple definition of %s." % (name))
		_TARGET_TYPES[name] = target_class
		return target_class

@WatchTarget.register
class FileWatchTarget():
	def __init__(self, file_regex):
		self._file_regex = file_regex

