# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from display import display_vote_bb
import errstr
from string import digits
from util import diff_strings

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

def multimerge(mapping, froms, tos):
	primary_to = tos[0]
	other_tos = tos[1:]

	# Validate first
	for from_vote in froms:
		for some_to in tos:
			if some_to==from_vote:
				raise CommandError(errstr.MERGE_TO_SELF)

		if mapping[primary_to].is_descendant_of(mapping[from_vote]):
			raise CommandError(errstr.MERGE_TO_DESCENDANT)

	# Now merge
	for from_vote in froms:
		for other_to in other_tos:
			mapping[other_to].copy(mapping[from_vote])

		mapping[primary_to].merge(mapping[from_vote])

# split_str is an array of strings
def parse_line_numbers(split_str, mapping, force_plural = False):
	try:
		out = [ int(i) for i in split_str ]
	except ValueError:
		if len(split_str) == 1 and not force_plural:
			raise CommandError(errstr.INVALID_INDEX)
		else:
			raise CommandError(errstr.INVALID_INDICES)

	for index in out:
		if index < 0 or index >= len(mapping):
			if len(split_str) == 1 and not force_plural:
				raise CommandError(errstr.INVALID_INDEX)
			else:
				raise CommandError(errstr.INVALID_INDICES)

	return out

def parse_line_number(str, mapping):
	try:
		out = int(str)
	except ValueError:
		raise CommandError(errstr.INVALID_INDEX)
	if out < 0 or out >= len(mapping):
		raise CommandError(errstr.INVALID_INDEX)
	return out

def wait_for_line(str=None):
	out = '[ENTER] to continue'
	if str:
		out = str + ' ' + out
	raw_input(out)

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

class Merge(Command):
	def names(self):
		return ['merge', 'm']
	def go(self, args, model):
		args = args.split()

		if len(args) != 2:
			raise CommandError(errstr.TOO_MANY_ARGUMENTS)

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
		model.mapping[idx].remove_self()
	def description(self):
		return 'Remove a line.'
	def usage(self):
		return ['remove 1']


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


class TypoJam(Command):
	def names(self):
		return ['typojam', 'tj']

	def go(self, args, model):
		mapping = model.mapping
		try:
			idx = int(args)
		except ValueError:
			raise CommandError(errstr.INVALID_INDEX)

		if idx<0 or idx >= len(mapping):
			raise CommandError(errstr.INVALID_INDEX)

		compare_raw = mapping[idx].primary_text.encode('utf-8')
		compare_munge = self.translate(mapping[idx])

		matches = []
		munge_ratios = { compare_munge: 1.0 }
		raw_diffs = { compare_raw: (compare_raw, 1.0) }

		parents = []
		parent = mapping[idx].parent
		while parent != None:
			parents.append(parent)
			parent = parent.parent

		for i in xrange(len(mapping)):
			if i == idx:
				continue

			i_raw = mapping[i].primary_text.encode('utf-8')
			i_munge = self.translate(mapping[i])

			if i_munge not in munge_ratios:
				munge_ratios[i_munge] = diff_strings(compare_munge, i_munge)[1]

			if i_raw not in raw_diffs:
				raw_diffs[i_raw] = diff_strings(compare_raw, i_raw)

			ratio = max(munge_ratios[i_munge], raw_diffs[i_raw][1])

			if ratio > 0.85:
				if mapping[i] in parents:
					print "Warning: Parent #%d matched, ignoring" % i
				else:
					matches.append((ratio, i, raw_diffs[i_raw][0]))

		matches.sort()
		matches.reverse()

		if len(matches) < 1:
				wait_for_line('No matches found.')
				return

		for ratio, i, plain_diff in matches:
			print '#%d (%4.1f%%) %s' % (i, 100*ratio, plain_diff)

		remove = raw_input(
			'Accept? (ENTER accepts all, none accepts none, or you can provide '+\
			'specific indices) '
		)
		if remove.strip().lower() == 'none':
			pass
		elif remove.strip() == '':
			for ratio, i, plain_diff in matches:
				mapping[idx].merge(mapping[i])
		else:
			ok_is = set([ i for ratio, i, plain_diff in matches ])

			if remove.find(',') == -1:
				remove = remove.split(' ')
			else:
				remove = remove.split(',')
			try:
				remove = [ int(a) for a in remove ]
			except ValueError:
				raise CommandError(errstr.INVALID_INDICES)
				return
			for value in remove:
				if value not in ok_is:
					print 'Warning: Couldn\'t resolve %d, not a found duplicate' % value
				else:
					mapping[idx].merge(mapping[value])

	TABLE = '????????????????????????????????????????????????????????????'+\
		'?????abcdefghijklmnopqrstuvwxyz??????abcdefghijklmnopqrstuvwxyz?????????'+\
		'????????????????????????????????????????????????????????????????????????'+\
		'????????????????????????????????????????????????????'
 	DELETE = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'+\
		'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'+\
		'\'()*+,-./0123456789:;<=>?@[\\]^_`{|}~\x7f\x80\x81\x82\x83\x84\x85\x86'+\
		'\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98'+\
		'\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa'+\
		'\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc'+\
		'\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce'+\
		'\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0'+\
		'\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2'+\
		'\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'

	def translate(self, vote):
		return vote.primary_text.encode('utf-8').translate(self.TABLE, self.DELETE)

	def description(self):
		return 'Try to find lines that are typos of a particular line, and help '+\
			'merge them together.'
	def usage(self):
		return ['typojam 1']


class SetMath(Command):
	def names(self):
		return ['setmath', 'sm']
	def go(self, args, model):
		mapping = model.mapping

		tokens = []
		i = 0
		while i < len(args):	# gah, I want a real for loop
			c = args[i]
			i+=1	# yuck, but this avoids bugs where I forget to i+=1...
			if c in ['(', ')', '+', '-', '&']:
				tokens.append((c, None))
			elif c in [ 'v', 'y', 'n', 'V', 'Y', 'N' ]:
				type = c.lower()
				# yank out the number
				digs = ''
				while i < len(args) and args[i] in digits:
					digs += args[i]
					i += 1
				if not len(digs):
					raise CommandError(errstr.SETMATH_LEX)
				digs = int(digs)

				if digs<0 or digs >= len(mapping):
					raise CommandError(errstr.INVALID_INDEX)

				if type == 'v':
					selected = mapping[digs].yea | mapping[digs].nay
				elif type == 'y':
					selected = mapping[digs].yea
				elif type == 'n':
					selected = mapping[digs].nay

				tokens.append(('set', selected))
			elif c == ' ':
				continue
			else:
				raise CommandError(errstr.SETMATH_LEX)

		left_operands = [ None ]
		operators = [ None ]

		for token, selected in tokens:
			if token == '(':
				if left_operands[-1] is not None and operators[-1] is None:
					raise CommandError(errstr.SETMATH_PARSE+' (Open Parenthesis)')
				left_operands.append(None)
				operators.append(None)
			elif token == ')':
				if len(left_operands) == 1 or left_operands[-1] is None:
					raise CommandError(errstr.SETMATH_PARSE+' (Close Parenthesis)')
				if len(operators) == 1 or operators[-1] is not None:
					raise CommandError(errstr.SETMATH_PARSE+' (Close Parenthesis)')
				result = left_operands[-1]
				left_operands = left_operands[:-1]
				operators = operators[:-1]

				if operators[-1] is not None:
					left_operands[-1] = \
						self.oper(left_operands[-1], operators[-1], result)
					operators[-1] = None
				else:
					left_operands[-1] = result
			elif token in ['+', '-', '&']:
				if left_operands[-1] is None:
					raise CommandError(errstr.SETMATH_PARSE+' (Operator)')
				operators[-1] = token
			elif token == 'set':
				if left_operands[-1] is None:
					left_operands[-1] = selected
				else:
					if operators[-1] is None:
						raise CommandError(errstr.SETMATH_PARSE+' (Set)')
					left_operands[-1] = \
						self.oper(left_operands[-1], operators[-1], selected)
					operators[-1] = None

		if len(left_operands) != 1 or operators[-1] is not None:
			raise CommandError(errstr.SETMATH_PARSE, '(Exit)')

		result = left_operands[-1]

		print ('Result (%d users): ' % len(result)) +', '.join(u for u in result)
		wait_for_line()

	def oper(self, left, oper, right):
		if oper == '&':
			return left & right
		elif oper == '+':
			return left | right
		elif oper == '-':
			return left - right
		else:
			assert False

	def description(self):
		return 'Calculate complex combinations of voters.'
	def usage(self):
		return ['setmath y1 - v2', 'setmath y1 & y2', 'setmath v0 - (n1 + n2 + n3)']
	def info(self):
		return """The setmath command performs basic set calculations on the sets \
of people who voted for or against different vote options. For example, if you
want to find everybody who voted for line 1, but neither for or against line 2,
you can use the command 'setmath y1 - v2'.

Operands:
  y1: All of the users who voted 'Yea' to line 1.
  n1: All of the users who voted 'Nay' to line 1.
  v1: All of the users who voted (either way) on line 1.

Operators:
  & (AND): Find all of the users in both of the two operands.
  + (OR): Find all of the users in either of the two operands.
  - (Difference): Find all of the users in the first operand but not the second.

All of setmath's operators have the same precedence; they're evaluated from \
left to right."""

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

class Help(Command):
	def names(self):
		return ['help', '?']
	def description(self):
		return 'Helps you figure out how to use Tabulon.'
	def info(self):
		return 'If you pass help the name of another command, it\'ll provide '+\
			'information about that specific command. If you don\'t, it\'ll list '+\
			'all of the commands.'
	def usage(self):
		return ['help', 'help multimerge']
	def go(self, args, model):
		global COMMANDS, COMMAND_LIST
		args = args.strip().lower()

		if args:
			if args not in COMMANDS:
				print errstr.UNKNOWN_COMMAND
				print 'Use help to list all the known command names.'
			else:
				command = COMMANDS[args]
				names = command.names()
				print names[0]
				if len(names)>1:
					print 'aka '+(', '.join(names[1:]))
				print
				print command.description()
				print
				print 'usage:'
				for usage in command.usage():
					print '  '+usage
				info = command.info()
				if info is not None:
					print
					print info
				print
		else:
			print 'Tabulon Commands:'
			print
			for command in COMMAND_LIST:
				names = command.names()

				out = '  '+names[0]
				if len(names) > 1:
					out += ' (aka '+(', '.join(names[1:]))+')'
				out += ': '+command.description()
				print out

			print
			print 'For more information on any particular command, call the help '+\
				'command with the name of the command as an argument. For example, '+\
				'"help multimerge."'
			print
		wait_for_line()

class Quit(Command):
	def names(self):
		return ['quit']
	def go(self, args, model):
		exit(0)
	def description(self):
		return 'Close Tabulon.'
	def usage(self):
		return ['quit']

COMMAND_LIST = [
	VoteOf(),
	Merge(),
	MultiMerge(),
	Blame(),
	Info(),
	Remove(),
	TypoJam(),
	SetMath(),
	BBCode(),
	Quit(),
	Help(),
]

def _generate_commands_array():
	global COMMANDS, COMMAND_LIST
	COMMANDS = {}
	for command in COMMAND_LIST:
		for name in command.names():
			name = name.lower()

			if name in COMMANDS:
				raise NameError('The name "'+name+'" is used by multiple commands!')
			COMMANDS[name] = command

_generate_commands_array()

def run_console_command(vote, mapping, command, v4u):
	global COMMANDS

	space = command.find(' ')
	args = ''
	if space!=-1:
		args = command[space+1:]
		command = command[:space]
	command = command.lower()

	if command in COMMANDS:
		try:
			COMMANDS[command].go(args, CommandModel(vote, mapping, v4u))
		except CommandError as e:
			print e
	else:
		print errstr.UNKNOWN_COMMAND
