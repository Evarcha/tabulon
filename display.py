# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from termutil import *
from sys import stdout

def display_vote(vote):
	return _display_vote(vote, [], 0)

def get_formatted_vote_line(vote, index=None, indent=0, text=None, extra=None):
	if text is None:
		text = vote.primary_text

	if extra is None:
		extra = ''

	spaces = '  '*indent
	plusminus =	\
		sgr(FG_GRN, BOLD)+(' +%-2d' % len(vote.yea)) +	\
		sgr(FG_RED, BOLD)+(' -%-2d '% len(vote.nay)) +	\
		sgr()
	if index is not None:
		number = '#'+str(index)
		if len(number) < 4:
			number += ' ' * ( 4 - len(number) )
	else:
		number = ''

	return spaces+number+extra+plusminus+text

def _display_vote(vote, mapping, indent):
	print get_formatted_vote_line(vote, len(mapping), indent)

	mapping.append(vote)

	for sub in vote.subs:
		_display_vote(sub, mapping, indent+1)

	return mapping

def get_vote_bb(vote):
	return _get_vote_bb(vote, [])

def _get_vote_bb(vote, mapping):
	plusminus =	\
		'[b][color=green]'+(' +%-2d' % len(vote.yea)) +	\
		'[/color][color=red]'+(' -%-2d '% len(vote.nay)) +	\
		'[/color][/b]'
	text = vote.primary_text
	number = '#' + str(len(mapping))

	out = number+plusminus+text

	mapping.append(vote)

	if len(vote.subs):
		out += '\n[indent]'
		for sub in vote.subs[:-1]:
			out += _get_vote_bb(sub, mapping)
			out += '\n'
		_get_vote_bb(vote.subs[-1], mapping)
		out += '[/indent]'

	return out

def get_blame_bb(mapping):
	out = '[spoiler=Details]'

	voters = mapping[0].yea | mapping[0].nay
	out += '[b]All Voters: ([/b]%d[b])[/b]' % len(voters)
	out += (', '.join(voters)).encode('utf-8')
	out += '\n\n'


	for i in xrange(1, len(mapping)):
		line = mapping[i]
		out += '[spoiler=#%d %s]\n' % (i, line.primary_text.replace(']', ''))

		out += '[b]Texts:[/b]'
		out += '[indent]'+line.primary_text+'\n'
		for text in line.texts - set([line.primary_text]):
			out += text+'\n'
		out += '[/indent]\n'

		out += '[b]Yeas: ([/b]%d[b])[/b]' % len(line.yea)
		out += (', '.join(line.yea)).encode('utf-8')
		out += '\n'

		out += '[b]Nays: ([/b]%d[b])[/b]' % len(line.nay)
		out += (', '.join(line.nay)).encode('utf-8')
		out += '\n'

		out += '[/spoiler]'
	return out + '[/spoiler]'
