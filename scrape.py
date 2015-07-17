# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

import re
from vote import MergeableVote
from util import *

####################################
## Maximum Page Number Extraction ##
####################################

# Get the maximum page number from a page
# Returns 1 if it can't find anything
def max_page_number_from_page(page):
	pagenavs = page.xpath('//div[@class=\'PageNav\']')
	if not pagenavs:
		return 1
	return int(pagenavs[0].get('data-last'))

#####################
## Post Extraction ##
#####################

class Post:
	def __init__(self, root):
		self.author = root.get('data-author')
		text_elem = root.xpath('div/div/article/blockquote')[0]
		for quote in text_elem.xpath('//blockquote[@class=\'quoteContainer\']'):
			quote.drop_tree()
		self.text = text_elem.text_content()
		self.id = int(root.get('id')[5:])
	def __repr__(self):
		return '<Post by '+repr(self.author)+': '+repr(self.text)+'>'

def posts_from_page(page):
	return [ Post(root) for root in page.xpath('.//li[@data-author]') ]

#################
## Vote Lexing ##
#################

VOTE_LINE_REGEX = re.compile(r"^(-+>?)?\[.*\].*$")

class VoteLine:
	def __init__(self, indent, type, text):
		self.indent = indent
		self.type = type
		self.text = text
	def __repr__(self):
		return '<VoteLine, l'+str(self.indent)+', type '+repr(self.type)+\
			', '+repr(self.text)+'>'
	def __str__(self):
		return ('-'*self.indent)+'['+self.type+'] '+self.text

def extract_vote_lines(text):
	lines = text.split('\n')
	out = []

	for line in lines:
		despace = line.replace(' ', '').replace('\t', '')
		if VOTE_LINE_REGEX.match(despace) == None:
			continue # this isn't a vote

		# Because of the regex and the space removal, this effectively counts the
		# dashes.
		indent_level = despace.find('[')

		# This is the text inside the brackets; e.g., 'X', 'Y', 'Q', 'N', ' '.
		vote_type = line[ line.find('[')+1 : line.find(']')]
		vote_type = vote_type.upper().strip()

		# This is the text of the vote itself.
		vote_text = line[ line.find(']')+1 : ]
		vote_text = vote_text.strip()

		out.append(VoteLine(indent_level, vote_type, vote_text))

	return out

##################
## Vote Parsing ##
##################

WARN_UNKNOWN_VOTE_TYPE = 'you used an unknown vote type'

POSITIVE_VOTE_LINE_TYPES = ['X', 'Y', '+']
NEGATIVE_VOTE_LINE_TYPES = ['N', '-']
IGNORED_VOTE_LINE_TYPES = ['Q', 'J', 'QN', 'JN', 'JK', '']
DISCOURAGED_VOTE_LINE_TYPES = { }
PROCESSED_VOTE_LINE_TYPES = POSITIVE_VOTE_LINE_TYPES + NEGATIVE_VOTE_LINE_TYPES
RECOGNIZED_VOTE_LINE_TYPES = PROCESSED_VOTE_LINE_TYPES + IGNORED_VOTE_LINE_TYPES

class ParsedVote(object):
	def __init__(self, text, parent):
		self.yea = set()
		self.nay = set()
		self.text = text
		self.subs = {}
		self.parent = parent
		self.mv = None
		self.mv_mode = False

	def get_votes(self):
		return self.yea, self.nay

	def vacate(self):
		self.yea = set()
		self.nay = set()
		for sub in self.subs.values():
			sub.vacate()

	def add_yea(self, username):
		self.yea.add(username)

	def add_nay(self, username):
		self.nay.add(username)

	def set_mv_mode(self, on):
		self.mv_mode = on
		self.mv = None
		for sub in self.subs.values():
			sub.set_mv_mode(on)

	def _set_mv(self, mv):
		assert not self.mv
		self.mv = mv

	def _get_mv(self):
		assert self.mv_mode
		if self.mv:
			return self.mv

		# if this particular node has no MV (let's say its MV was deleted) then use
		# the parent's MV (and recur if needed...)
		return self.parent._get_mv()

	def navigate(self, text):
		if text not in self.subs:
			self.subs[text] = new_iv = ParsedVote(text, self)

			if self.mv_mode:
				# need to make a new mergeable vote as well
				mv = self._get_mv()
				new_mv = MergeableVote(new_iv, None)
				mv.add(new_mv)

				# set up mv mode on the new iv, otherwise children of newly added ivs
				# won't get mvs and everything will be terrible
				new_iv.set_mv_mode(True)
				new_iv._set_mv(new_mv)

		return self.subs[text]

	def __repr__(self):
		return ('<ParsedVote +%d -%d ' % (len(self.yea), len(self.nay)))+	\
			repr(self.text)+': '+ repr(uniq(self.subs.values()))+'>'

def iv_setup_mv_mode(iv_root, mv_root):
	iv_root.set_mv_mode(True)
	mv_root._mark_ivs()

# returns a tuple: (freeform, votes_from_person)
def process_vote_from_posts(posts, freeform=None, mergeable=None):
	if freeform is None:
		freeform = ParsedVote('Freeform', None)
	else:
		freeform.vacate()

	if mergeable is not None:
		iv_setup_mv_mode(freeform, mergeable)
	errors = {}

	vote_posts = []

	# figure out which posts have votes, extract the vote lines
	for post in posts:
		vote_lines = extract_vote_lines(post.text)

		bad_vote_line_type = False
		for line in vote_lines:
			if line.type not in RECOGNIZED_VOTE_LINE_TYPES:
				bad_vote_line_type = True
				break

		vote_lines = \
			[ line for line in vote_lines if line.type in PROCESSED_VOTE_LINE_TYPES ]

		errors[post.author] = set()
		if not len(vote_lines):
			if bad_vote_line_type:
				if post.author in errors:
					errors[post.author].add(WARN_UNKNOWN_VOTE_TYPE)
				else:
					errors[post.author] = set(WARN_UNKNOWN_VOTE_TYPE)
			continue

		if bad_vote_line_type:
			errors[post.author].add(WARN_UNKNOWN_VOTE_TYPE)

		for type in set(line.type for line in vote_lines):
			if type in DISCOURAGED_VOTE_LINE_TYPES:
				errors[post.author].add(DISCOURAGED_VOTE_LINE_TYPES[type])

		vote_posts.append((vote_lines, post))

	# figure out what each user's last vote post is
	last_post_ids_for_user = {}
	for vote_lines, post in vote_posts:
		# I don't have to explicitly invalidate old post IDs - they'll get
		# overwritten on their own
		last_post_ids_for_user[post.author] = post.id

	last_votes_from_person = {}
	# do the final parse
	for vote_lines, post in vote_posts:
		freeform.add_yea(post.author)
		munged_author = post.author.lower().replace(' ', '')

		# check for a bandwagon vote
		text = vote_lines[0].text.lstrip('@').rstrip('.!')
		text = text.lower().replace(' ', '')
		if text in last_votes_from_person and text != munged_author and \
			vote_lines[0].type in POSITIVE_VOTE_LINE_TYPES:
			
			vote_lines = last_votes_from_person[text] + vote_lines[1:]

		# store the current vote (with bandwagon alterations)
		last_votes_from_person[munged_author] = vote_lines

		if post.id != last_post_ids_for_user[post.author]:
			# Since this isn't the voter's final vote, we don't need to process it
			# any farther
			continue

		indents = [-1]
		pos = freeform
		for line in vote_lines:
			while line.indent <= indents[-1]:
				indents = indents[:-1]
				pos = pos.parent

			pos = pos.navigate(line.text)
			if line.type in POSITIVE_VOTE_LINE_TYPES:
				pos.add_yea(post.author)
			elif line.type in NEGATIVE_VOTE_LINE_TYPES:
				pos.add_nay(post.author)
			else:
				raise AssertionError(
					'There\'s a vote type that isn\'t positive or negative, but '+ \
					'wasn\'t filtered!'
				)

			if line.indent > indents[-1]:
				indents.append(line.indent)

	freeform.set_mv_mode(False)

	if mergeable is None:
		mergeable = MergeableVote(freeform, None)
	else:
		mergeable.recompute_votes()

	return (mergeable, freeform, last_votes_from_person)
