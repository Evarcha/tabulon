# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
from termutil import CLEAR_DISPLAY
import tboard
from display import get_vote_bb, get_blame_bb, display_vote
import errstr

##########################
## Information Commands ##
##########################

# All of the simple commands for displaying additional information go here.

class AlphaShow(Command):
	def names(self):
		return ['alpha', 'as']
	def go(self, args, model):
		print
		alpha = sorted(model.mapping[1:], key=lambda x: x.primary_text.upper())
		show_sorted_vote(model.mapping, alpha)
		print
		wait_for_line()
	def description(self):
		return 'Print the vote sorted alphabetically.'
	def usage(self):
		return ['alpha']

class ShowHidden(Command):
	def names(self):
		return ['showhidden', 'shh']
	def go(self, args, model):
		print CLEAR_DISPLAY
		hidden_mapping = display_vote(model.vote, True)
		print

		while True:
			remove = raw_input('Unhide? ')
			if not remove.strip():
				break

			vote = parse_line_number(remove, hidden_mapping)
			hidden_mapping.unhide[vote]
	def description(self):
		return 'Show the vote with "hidden" vote lines included.'
	def usage(self):
		return ['showhidden']

class VoteOf(Command):
	def names(self):
		return ['voteof', 'vo']
	def go(self, args, model):
		name = args.lower().replace(' ', '')
		if name not in model.votes_for_user:
			raise CommandError(errstr.UNKNOWN_USER)
		for line in model.votes_for_user[name]:
			print line
		print
		wait_for_line()
	def description(self):
		return 'Get an user\'s vote.'
	def usage(self):
		return ['voteof BeaconHill']

class Blame(Command):
	def names(self):
		return ['blame', 'b']
	def go(self, args, model):
		idx = parse_line_number(args, model.mapping)
		line = model.mapping[idx]

		print 'Yeas: (%d)' % len(line.yea), ', '.join(line.yea)
		print 'Nays: (%d)' % len(line.nay), ', '.join(line.nay)
		wait_for_line()
	def description(self):
		return 'List everyone who voted for a particular line.'
	def usage(self):
		return ['blame 1']

class Info(Command):
	def names(self):
		return ['info', 'i']
	def go(self, args, model):
		idx = parse_line_number(args, model.mapping)
		line = model.mapping[idx]

		print line.primary_text
		for text in line.texts - set([line.primary_text]):
			print text
		print

		print 'Yeas: (%d)' % len(line.yea), ', '.join(line.yea)
		print 'Nays: (%d)' % len(line.nay), ', '.join(line.nay)
		wait_for_line()
	def description(self):
		return 'Show all of the alternate text options for a line, and everyone '+\
			'who voted for it.'
	def usage(self):
		return ['info 1']

class BBCode(Command):
	def names(self):
		return ['bbcode', 'bb']
	def go(self, args, model):
		print
		print get_vote_bb(model.vote)
		print

		wait_for_line()
	def description(self):
		return 'Print out the vote in BBCode.'
	def usage(self):
		return ['bbcode']

class BBCodeExtended(Command):
	def names(self):
		return ['bbblame', 'bbx']
	def go(self, args, model):
		print
		print get_vote_bb(model.vote)
		print
		print get_blame_bb(model.mapping)
		print

		wait_for_line()
	def description(self):
		return 'Print out the vote in BBCode, with an extra spoilered Details '+\
			'section providing more information.'
	def usage(self):
		return ['bbblame']

class BBCodeCopy(Command):
	def names(self):
		return ['copybbcode', 'cbb']
	def go(self, args, model):
		tboard.copy(get_vote_bb(model.vote))
	def description(self):
		return 'Copy the vote, formatted in BBCode, to the clipboard.'
	def usage(self):
		return ['copybbcode']
	def unlisted(self):
		return not tboard.available()

class BBCodeCopyExtended(Command):
	def names(self):
		return ['copybbblame', 'cbbx']
	def go(self, args, model):
		tboard.copy(get_vote_bb(model.vote)+'\n\n'+get_blame_bb(model.mapping))
	def description(self):
		return 'Copy the vote, formatted in BBCode, to the clipboard, with an '+\
			'extra spoilered Details section providing more information.'
	def usage(self):
		return ['copybbblame']
	def unlisted(self):
		return not tboard.available()
