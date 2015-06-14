# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from termutil import *
from sys import stdout

def display_vote(vote):
	return _display_vote(vote, [], 0)

def _display_vote(vote, mapping, indent):
	spaces = '  '*indent
	plusminus =	\
		sgr(FG_GRN, BOLD)+(' +%-2d' % len(vote.yea)) +	\
		sgr(FG_RED, BOLD)+(' -%-2d '% len(vote.nay)) +	\
		sgr()
	text = vote.primary_text
	number = ('#%d   ' % len(mapping))[:max(4, len(str(len(mapping))))]

	print spaces+number+plusminus+text

	mapping.append(vote)

	for sub in vote.subs:
		_display_vote(sub, mapping, indent+1)

	return mapping

def display_vote_bb(vote):
	out = _display_vote_bb(vote, [])
	stdout.write('\n')
	stdout.flush()
	return out

def _display_vote_bb(vote, mapping):
	plusminus =	\
		'[b][color=green]'+(' +%-2d' % len(vote.yea)) +	\
		'[/color][color=red]'+(' -%-2d '% len(vote.nay)) +	\
		'[/color][/b]'
	text = vote.primary_text
	number = '#' + str(len(mapping))

	stdout.write(number+plusminus+text)

	mapping.append(vote)

	if len(vote.subs):
		stdout.write('\n[indent]')
		for sub in vote.subs[:-1]:
			_display_vote_bb(sub, mapping)
			stdout.write('\n')
		_display_vote_bb(vote.subs[-1], mapping)
		stdout.write('[/indent]')

	return mapping
