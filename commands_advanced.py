# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
from util import *
import errstr
from setmath import setmath

#######################
## Advanced Commands ##
#######################

# All the advanced commands go in here. These are a little ill-defined, but
# generally if they're not porcelain around a few simple library commands
# they belong here.

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
					warning('Parent #%d matched, ignoring' % i)
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
					warning('Couldn\'t resolve %d, not a found duplicate' % value)
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
		def set_callback(type, digs):
			type = type.lower()
			if type not in 'vyn':
				return None

			digs = parse_line_number(digs, model.mapping)

			if type == 'v':
				return model.mapping[digs].yea | model.mapping[digs].nay
			elif type == 'y':
				return model.mapping[digs].yea
			elif type == 'n':
				return model.mapping[digs].nay

		result = setmath(args, set_callback)

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
		return """The setmath command performs basic set calculations on the sets
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

class RegexMoveRename(Command):
	def names(self):
		return ['moveregex', 'vr']
	def description(self):
		return 'Move and rename items according to a regex.'
	def usage(self):
		return [
			r"rmove r0 1 /^Flee (east|west)!/Run \1!/",
			'rmove R0-r26 27 '+\
				r"/Tay?lor's (?:cape )?name [sa]hould be ([^.]*)\.?/\1/"
		]
	def go(self, args, model):
		slashpos = args.find('/')
		if slashpos < 0:
			raise CommandError(errstr.FIND_REPLACE_BAD_FORMAT)
		regex = args[slashpos:].strip()
		args = args[:slashpos]

		space_pos = args.strip().rfind(' ')
		if space_pos < 0:
			raise CommandError(errstr.TOO_FEW_ARGUMENTS)

		equation = args[:space_pos]
		dest_idx = parse_line_number(args[space_pos:], model.mapping)
		destination = model.mapping[dest_idx]

		froms = parse_line_numbers_with_expands(equation, model.mapping)
		initial_length = len(froms)
		froms = filter(
			lambda x: (not destination.is_descendant_of(x)) and x != destination,
			froms
		)

		if initial_length > len(froms):
			warning( \
				'%d items removed for being ancestors of the destination. %d remain.'\
					% ( initial_length - len(froms), len(froms) )\
			)

		found = find_replace_regex(regex, froms)

		for vote in found:
			destination.add(vote)
	def info(self):
		return """The moveregex command finds all vote lines in the specified
search area that match a given regex. It renames them according to that regex,
and moves them to the desired destination.

The first argument to moveregex is an equation in setmath notation describing
which vote lines to search in the regex. The string 'r0' matches everything.
See the setmath documentation for more information on the format. Available
operands are r#, which matches recursively everything underneath the given node
number, R#, which is like r# but doesn't actually match the given node, c#,
which only matches the immediate children of the immediate node number, C#,
which is to c# as R# is to r#, and just a bare node number, which will match
only that node.

The second argument to moveregex is the line number of the node to move all of
the matches to.

The third argument to moveregex is the regex. This regex has two parts; it's
split like /find/replace/. Explaining regexes is outside of the scope of this
documentation, but you can find Python's documentation on regular expressions
at https://docs.python.org/2/library/re.html."""
