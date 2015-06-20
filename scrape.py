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

POSITIVE_VOTE_LINE_TYPES = ['X', 'Y']
NEGATIVE_VOTE_LINE_TYPES = ['N']
IGNORED_VOTE_LINE_TYPES = ['Q', 'J', 'QN', 'JN', 'JK', '']
DISCOURAGED_VOTE_LINE_TYPES = { }
PROCESSED_VOTE_LINE_TYPES = POSITIVE_VOTE_LINE_TYPES + NEGATIVE_VOTE_LINE_TYPES
RECOGNIZED_VOTE_LINE_TYPES = PROCESSED_VOTE_LINE_TYPES + IGNORED_VOTE_LINE_TYPES

class ParsedVote:
	def __init__(self, text, parent):
		self.yea = set()
		self.nay = set()
		self.text = text
		self.subs = {}
		self.parent = parent

	def vacate(self, username):
		if username in self.yea or username in self.nay:
			for sub in uniq(self.subs.values()):
				sub.vacate(username)
		if username in self.yea:
			self.yea.remove(username)
		if username in self.nay:
			self.nay.remove(username)

	def add_yea(self, username):
		self.yea.add(username)

	def add_nay(self, username):
		self.nay.add(username)

	def navigate(self, text):
		if text not in self.subs:
			self.subs[text] = ParsedVote(text, self)
		return self.subs[text]

	def __repr__(self):
		return ('<ParsedVote +%d -%d ' % (len(self.yea), len(self.nay)))+	\
			repr(self.text)+': '+ repr(uniq(self.subs.values()))+'>'

# returns a tuple: (freeform, votes_from_person)
def process_vote_from_posts(posts):
	freeform = ParsedVote('Freeform', None)
	last_votes_from_person = {}
	errors = {}

	for post in posts:
		vote_lines = extract_vote_lines(post.text)

		bad_vote_line_type = False
		for line in vote_lines:
			if line.type not in RECOGNIZED_VOTE_LINE_TYPES:
				bad_vote_line_type = True
				break

		vote_lines = \
			[ line for line in vote_lines if line.type in PROCESSED_VOTE_LINE_TYPES ]

		if not len(vote_lines):
			if bad_vote_line_type:
				if post.author in errors:
					errors[post.author].add(WARN_UNKNOWN_VOTE_TYPE)
				else:
					errors[post.author] = set(WARN_UNKNOWN_VOTE_TYPE)
			continue

		errors[post.author] = set()
		if bad_vote_line_type:
			errors[post.author].add(WARN_UNKNOWN_VOTE_TYPE)
		freeform.vacate(post.author)
		freeform.add_yea(post.author)

		for type in set(line.type for line in vote_lines):
			if type in DISCOURAGED_VOTE_LINE_TYPES:
				errors[post.author].add(DISCOURAGED_VOTE_LINE_TYPES[type])

		if len(vote_lines) >= 1:
			# check for a bandwagon vote
			text = vote_lines[0].text.lstrip('@').rstrip('.!')
			text = text.lower().replace(' ', '')
			if text in last_votes_from_person and \
				text != post.author.lower().replace(' ', ''):

				vote_lines = last_votes_from_person[text] + vote_lines[1:]
		last_votes_from_person[post.author.lower().replace(' ', '')] = vote_lines

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
	return (MergeableVote(freeform, None), last_votes_from_person)
