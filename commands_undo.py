# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
import errstr
from copy import deepcopy

#################
## Undo / Redo ##
#################

class UndoStack(object):
	def __init__(self, vote):
		self.undo_list = []
		self.redo_list = []
		self.current_copy = deepcopy(vote)
		self.current = vote
		vote._set_stack(self)
		self.is_dirty = False
	def dirty(self):
		self.is_dirty = True
	def update(self):
		if self.is_dirty:
			self.is_dirty = False
			self.undo_list.append(self.current_copy)
			self.redo_list = []
			self.current._set_stack(None)
			self.current_copy = deepcopy(self.current)
			self.current._set_stack(self)
	def undo(self):
		assert len(self.undo_list) > 0
		assert not self.is_dirty
		new = self.undo_list[-1]
		self.undo_list = self.undo_list[:-1]
		self.redo_list.append(self.current_copy)
		self.current_copy = deepcopy(new)
		self.current = new
		self.current._set_stack(self)
		self.current.defrost()
		return self.current
	def redo(self):
		assert len(self.redo_list) > 0
		assert not self.is_dirty
		new = self.redo_list[-1]
		self.redo_list = self.redo_list[:-1]
		self.undo_list.append(self.current_copy)
		self.current_copy = deepcopy(new)
		self.current = new
		self.current._set_stack(self)
		self.current.defrost()
		return self.current
	def has_undo(self):
		return len(self.undo_list) > 0
	def has_redo(self):
		return len(self.redo_list) > 0

class Undo(Command):
	def names(self):
		return ['undo', 'uu']
	def description(self):
		return 'Undo the last command that changed the vote state.'
	def usage(self):
		return ['undo']
	def go(self, args, model):
		if len(args):
			raise CommandError(errstr.NO_ARGUMENTS_NEEDED)
		if not model.undo_stack.has_undo():
			raise CommandError(errstr.NOTHING_TO_UNDO)
		model.vote = model.undo_stack.undo()

class Redo(Command):
	def names(self):
		return ['redo', 'rr']
	def description(self):
		return 'Undo the last command that changed the vote state.'
	def usage(self):
		return ['redo']
	def go(self, args, model):
		if len(args):
			raise CommandError(errstr.NO_ARGUMENTS_NEEDED)
		if not model.undo_stack.has_redo():
			raise CommandError(errstr.NOTHING_TO_REDO)
		model.vote = model.undo_stack.redo()
