# -*- coding: utf-8 -*-
"""
Implementation of the XDG MIME actions draft
http://www.freedesktop.org/wiki/Specifications/mime-actions-spec
"""

from . import xdg

ADDED_ASSOCIATIONS = "Added Associations"
REMOVED_ASSOCIATIONS = "Removed Associations"
DEFAULT_APPLICATIONS = "Default Applications"

class ActionsFile(xdg.IniFile):
	"""
	~/.local/share/applications/mimeapps.list
	"""

	def __init__(self):
		super(ActionsFile, self).__init__()
		self.keys = {
			ADDED_ASSOCIATIONS: {},
			REMOVED_ASSOCIATIONS: {},
			DEFAULT_APPLICATIONS: {},
		}

	def _parseAssociations(self, key):
		from .mime import MimeType
		d = self.keys[key]

		for mime, apps in self.cfg.items(key):
			# First, check for aliases and unalias anything we find
			# see http://lists.freedesktop.org/archives/xdg/2010-March/011336.html
			alias = MimeType(mime).aliasOf()
			if alias:
				mime = alias

			if mime not in d:
				d[mime] = []
			assert apps.endswith(";"), apps
			apps = apps.split(";")
			for app in apps:
				if not app:
					# We either got two semicolons in a row
					# or we got the last semicolon
					continue
				d[mime].insert(0, app)

	def parseKeys(self):
		self._parseAssociations(ADDED_ASSOCIATIONS)
		self._parseAssociations(REMOVED_ASSOCIATIONS)

		# Default apps are not lists
		for mime, app in self.cfg.items(DEFAULT_APPLICATIONS):
			# Check if the desktop file exists
			if xdg.getDesktopFilePath(app):
				self.keys[DEFAULT_APPLICATIONS][mime] = app

	def addedAssociations(self, mime):
		return self.keys[ADDED_ASSOCIATIONS].get(mime)

	def removedAssociations(self, mime):
		return self.keys[REMOVED_ASSOCIATIONS].get(mime)

	def defaultApplication(self, mime):
		return self.keys[DEFAULT_APPLICATIONS].get(mime)

ACTIONS = ActionsFile()
for f in xdg.getFiles("applications/mimeapps.list"):
	ACTIONS.parse(f)


class CacheFile(xdg.IniFile):
	"""
	applications/mimeinfo.cache
	Not part of the spec, but generated by desktop-file-utils
	"""

	def parseKeys(self):
		for mime, apps in self.cfg.items("MIME Cache"):
			if mime not in self.keys:
				self.keys[mime] = []

			assert apps.endswith(";"), apps
			apps = apps.split(";")
			for app in apps:
				if not app:
					# We either got two semicolons in a row
					# or we got the last semicolon
					continue
				self.keys[mime].insert(0, app)

CACHE = CacheFile()
for f in xdg.getFiles("applications/mimeinfo.cache"):
	CACHE.parse(f)
