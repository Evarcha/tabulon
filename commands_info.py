# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
from display import display_vote_bb
import errstr

##########################
## Information Commands ##
##########################

# All of the simple commands for displaying additional information go here.

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
		display_vote_bb(model.vote)
		print
		wait_for_line()
	def description(self):
		return 'Print out the vote in BBCode, fit for copy-pasting.'
	def usage(self):
		return ['bbcode']

class BBCodeExtended(Command):
	def names(self):
		return ['bbext', 'bbx']
	def go(self, args, model):
		print
		mapping = display_vote_bb(model.vote)
		print
		print '[spoiler=Details]'

		voters = model.vote.yea | model.vote.nay
		print '[b]All Voters: ([/b]%d[b])[/b]' % len(voters), ', '.join(voters)
		print

		for i in xrange(1, len(mapping)):
			line = mapping[i]
			print '[spoiler=#%d %s]' % (i, line.primary_text.replace(']', ''))

			print '[b]Texts:[/b]'
			print '[indent]'+line.primary_text
			for text in line.texts - set([line.primary_text]):
				print text
			print '[/indent]'

			print '[b]Yeas: ([/b]%d[b])[/b]' % len(line.yea), ', '.join(line.yea)
			print '[b]Nays: ([/b]%d[b])[/b]' % len(line.nay), ', '.join(line.nay)

			print '[/spoiler]'
		print '[/spoiler]'

		print

		wait_for_line()
	def description(self):
		return 'Print out the vote in BBCode, fit for copy-pasting, with an '+\
			'extra spoilered Details section providing more information.'
	def usage(self):
		return ['bbx']
