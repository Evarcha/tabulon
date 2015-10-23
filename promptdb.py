#!/usr/bin/python
# Prompts database
# Very simple, very hacky, hopefully functional.

import json
from sys import argv
from time import time
from random import randint
from os.path import isfile
from termutil import *
from math import *
import tboard
from bbcode import bb_format_sgr, bb_read_quote_elements

assert len(argv)==2, 'Need a command!'

site_expansions = {
	'SB': 'SpaceBattles',
	'SV': 'Sufficient Velocity',
	'QQ': 'Questionable Questing'
}

def expand_site(site):
	if not site:
		return ''
	site = idx(site_expansions, site, site)
	return 'on '+site

def idx(dictionary, key, default=None):
	if key in dictionary:
		return dictionary[key]
	return default

def adx(dictionary, key, value, default):
	if value != default:
		dictionary[key] = value

def new_prompt(poster, text, site, postno=None):
	prompts.append(Prompt({
		'poster': poster,
		'text': text,
		'site': site,
		'time': time(),
		'postno': postno
	}))

def binsearch(v, lo, hi, x):
	mid = (lo+hi)/2

	if lo==mid:
		return v[lo][2]
	
	if v[mid][0] >= x and v[mid][0] - v[mid][1] < x:
		return v[mid][2]
			
	if v[mid][0] > x:
		return binsearch(v, lo, mid, x)
	else:
		return binsearch(v, mid, hi, x)

def random_slotted_prompt(sps):
	idx = randint(1, sps[-1][0])
	return binsearch(sps, 0, len(sps), idx)

def slot_prompts():
	slotted_prompts = []
	n = 0
	for prompt in prompts:
		if prompt.used:
			continue
		n += prompt.slots()
		slotted_prompts.append((n, prompt.slots(), prompt))
	return slotted_prompts

class Prompt(object):
	def __init__(self, entry):
		self.poster = entry['poster']
		self.site = entry['site']
		self.text = entry['text']
		self.time = entry['time']
		self.seen = idx(entry, 'seen', self.time)
		self.score = idx(entry, 'score', 0)
		self.postno = idx(entry, 'postno')
		
		if self.score>10:
			self.score = 10
		if self.score<-10:
			self.score = -10
		
		self.used = idx(entry, 'used', False)
		self.usedWhen = idx(entry, 'usedWhen')
	def upvote(self):
		if self.score < 10:
			self.score += 1
	def downvote(self):
		if self.score > -10:
			self.score -= 1
	def use(self):
		if self.used:
			return
		self.used = True
		self.usedWhen = time()
	def slots(self):
		return 15+self.score+self.timescore()
	def see(self):
		self.seen = time()
	def timescore(self):
		return min(
			10,
			floor(log(( time() - self.seen ) / ( 60*60*24.0 ))/log(1.614))
		)
	def printBBCode(self):
		print '[quote='+self.poster+expand_site(self.site)+']'+self.text+'[/quote]'
	def makeEntry(self):
		out = {
			'poster': self.poster,
			'site': self.site,
			'text': self.text,
			'time': self.time
		}
		adx(out, 'seen', self.seen, self.time)
		adx(out, 'score', self.score, 0)
		adx(out, 'used', self.used, False)
		adx(out, 'usedWhen', self.usedWhen, None)
		adx(out, 'postno', self.postno, None)
		return out
	def display(self):
		if self.site:
			if self.site == 'SV':
				decorated_site = sgr(BOLD, FG_HCYN)+self.site+sgr()
			elif self.site == 'SB':
				decorated_site = sgr(BOLD, FG_HYEL)+self.site+sgr()
			else:
				decorated_site = sgr(BOLD)+self.site+sgr()
	
			print sgr(BOLD)+self.poster+sgr(), 'on', decorated_site
		else:
			print sgr(BOLD)+self.poster+sgr()
		print bb_format_sgr(self.text)
		print
		if self.score < -1:
			scorecolor = sgr(FG_HRED, BOLD)
		elif self.score > 1:
			scorecolor = sgr(FG_HGRN, BOLD)
		else:
			scorecolor = sgr(FG_HYEL, BOLD)
		scoretext = str(self.score)
		if self.score >= 0:
			scoretext = '+'+scoretext
		print scorecolor+scoretext+sgr()

PROMPTFILE = 'allprompts.json'

if isfile(PROMPTFILE):
	promptdb = json.load(open(PROMPTFILE))
else:
	promptdb = []
prompts = [ Prompt(entry) for entry in promptdb ]

cmd = argv[1].lower().strip()
if cmd == 'add':
	try:
		while True:
			poster = raw_input('Poster: ')
			text = raw_input('Text: ')
			site = raw_input('Site: ').upper().strip()
			new_prompt(poster, text, site)
			print 'OK, more? (CTRL-C to escape)'
	except KeyboardInterrupt:
		pass
elif cmd == 'import':
	assert tboard.available(), "Can't load prompts from clipboard!"

	site = raw_input('Site: ').upper().strip()
	raw_input('Press ENTER when ready.')
	
	imported = set(bb_read_quote_elements(tboard.paste()))
	
	for poster, postno, text in imported:
		new_prompt(poster, text, site, postno)
elif cmd == 'get':
	try:
		while True:
			slotted_prompts = slot_prompts()
			
			if not len(slotted_prompts):
				print 'No unused prompts!'
				exit(0)
		
			prompt = random_slotted_prompt(slotted_prompts)
			prompt.display()
			prompt.see()
			while True:
				cmd = raw_input('? ').lower().strip()
				if cmd in ['u', 'up']:
					prompt.upvote()
				elif cmd in ['d', 'dn', 'down']:
					prompt.downvote()
				elif cmd in ['p', 'pass', '']:
					pass
				elif cmd in ['t', 'tk', 'take']:
					prompt.use()
					prompt.printBBCode()
				else:
					continue
				break
			if prompt.used:
				break
	except KeyboardInterrupt:
		pass
else:
	raise 'Bad command given!'

promptdb = [ prompt.makeEntry() for prompt in prompts ]
json.dump(promptdb, open(PROMPTFILE, 'w'), indent=2)