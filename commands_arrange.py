# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
import errstr
from vote import MergeableVote

##########################
## Arrangement Commands ##
##########################

# All of the simple commands for arranging (merging, moving, adding, etc.)
# votes go in here.

class Merge(Command):
	def names(self):
		return ['merge', 'm']
	def go(self, args, model):
		args = args.split()

		if len(args) > 2:
			raise CommandError(errstr.TOO_MANY_ARGUMENTS)
		elif len(args) < 2:
			raise CommandError(errstr.TOO_FEW_ARGUMENTS)

		from_idx, to_idx = parse_line_numbers(args, model.mapping)

		multimerge(model.mapping, [from_idx], [to_idx])
	def description(self):
		return 'Merge two votes together.'
	def usage(self):
		return ['merge 1 2']

class MultiMerge(Command):
	def names(self):
		return ['multimerge', 'mm']

	def go(self, args, model):
		arrow = args.find('>')
		if arrow < 0:
			raise CommandError(errstr.MULTIMERGE_NEEDS_ARROW)

		froms = parse_line_numbers(args[:arrow].split(), model.mapping, True)
		tos = parse_line_numbers(args[arrow+1:].split(), model.mapping, True)

		multimerge(model.mapping, froms, tos)

	def description(self):
		return 'Merge multiple votes into multiple votes.'
	def usage(self):
		return ['multimerge 1 2 > 3']

class Remove(Command):
	def names(self):
		return ['remove', 'r']

	def go(self, args, model):
		idx = parse_line_number(args, model.mapping)
		if not model.mapping[idx].parent:
			raise CommandError(errstr.CANT_REMOVE_ROOT_NODE)
		model.mapping[idx].remove_self()
	def description(self):
		return 'Remove a line.'
	def usage(self):
		return ['remove 1']

class Add(Command):
	def names(self):
		return ['add', 'a']
	def description(self):
		return 'Add a new vote option.'
	def usage(self):
		return ['add 0 New top-level voting option']
	def go(self, args, model):
		args = args.split(None, 1)
		idx = parse_line_number(args[0], model.mapping)
		if len(args)<2:
			raise CommandError(errstr.ADD_NEEDS_TEXT)
		vote = MergeableVote(text=args[1].strip())
		model.mapping[idx].add(vote)

class Move(Command):
	def names(self):
		return ['move', 'v']
	def description(self):
		return 'Move a vote option to a different parent.'
	def usage(self):
		return ['move 1 2']
	def go(self, args, model):
		args = args.split()

		if len(args) > 2:
			raise CommandError(errstr.TOO_MANY_ARGUMENTS)
		elif len(args) < 2:
			raise CommandError(errstr.TOO_FEW_ARGUMENTS)

		from_idx, to_idx = parse_line_numbers(args, model.mapping)
		move(model.mapping, from_idx, to_idx)

class Rename(Command):
	def names(self):
		return ['rename', 'n']
	def description(self):
		return 'Set an existing vote option to have a new name.'
	def usage(self):
		return ['rename 1 Kick Kyubey']
	def go(self, args, model):
		args = args.split(None, 1)
		idx = parse_line_number(args[0], model.mapping)
		if len(args)<2:
			raise CommandError(errstr.RENAME_NEEDS_TEXT)
		model.mapping[idx].rename(args[1].strip())

class MoveRename(Command):
	def names(self):
		return ['moverename', 'vn']
	def description(self):
		return 'Move a vote option and rename it at the same time.'
	def usage(self):
		return ['nmove 1 2 Release the BEES!']
	def go(self, args, model):
		args = args.split(None, 2)
		if len(args)<2:
			raise CommandError(errstr.TOO_FEW_ARGUMENTS)
		elif len(args)<3:
			raise CommandError(errstr.RENAME_NEEDS_TEXT)
		from_idx, to_idx = parse_line_numbers(args[:2], model.mapping)
		move(model.mapping, from_idx, to_idx)
		model.mapping[from_idx].rename(args[2].strip())

class Trickle(Command):
	def names(self):
		return ['trickle', 't']
	def description(self):
		return '"Trickle down" votes from this vote\'s children.'
	def usage(self):
		return ['trickle 1']
	def go(self, args, model):
		args = args.split(None, 1)
		idx = parse_line_number(args[0], model.mapping)
		model.mapping[idx].trickle()

class Invert(Command):
	def names(self):
		return ['invert', 'iv']
	def description(self):
		return 'Invert a vote\'s yeas and nays. Used when merging a vote with its opposite.'
	def usage(self):
		return ['invert 1']
	def go(self, args, model):
		idx = parse_line_number(args, model.mapping)
		model.mapping[idx].invert()

class Recompute(Command):
	def names(self):
		return ['recompute']
	def description(self):
		return 'Recompute vote totals from IVs. For testing only.'
	def usage(self):
		return ['recompute']
	def go(self, args, model):
		model.vote.recompute_votes()
	def unlisted(self):
		return True
