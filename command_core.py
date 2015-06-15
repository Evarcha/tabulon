# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

class CommandError(Exception):
	def __init__(self, *args):
		self.message = ' '.join([str(a) for a in args])
	def __str__(self):
		return self.message

class CommandModel(object):
	def __init__(self, vote, mapping, votes_for_user):
		self.vote = vote
		self.mapping = mapping
		self.votes_for_user = votes_for_user

class Command(object):
	def names(self):
		raise NotImplementedError('Need to implement Command.names().')
	def go(self, args, model):
		raise NotImplementedError('Need to implement Command.go().')
	def description(self):
		# one-line information about this command
		raise NotImplementedError('Need to implement Command.description().')
	def usage(self):
		# return a list
		raise NotImplementedError('Need to implement Command.usage().')
	def info(self):
		# return a long (potentially with newlines) description of this command
		# or None
		return None
