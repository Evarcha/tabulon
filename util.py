# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

import re
import urlparse
from sys import stdout
from termutil import *
import difflib

#########################
## Miscellaneous Utils ##
#########################

def uniq(a):
	return list(set(a))

def url_get_domain(url):
	return urlparse.urlparse(url).netloc

# returns a pretty terminal-colored diff and a similarity ratio
def diff_strings(a, b):
	sm = difflib.SequenceMatcher(None, a, b, False)

	orig_ops = sm.get_opcodes()
	ops = []
	for op, i1, i2, j1, j2 in orig_ops:
		if op!='replace':
			ops.append((op, i1, i2, j1, j2))
		else:
			ops.append(('delete', i1, i2, j1, j1))
			ops.append(('insert', i1, i1, j1, j2))

	out = ""
	for op, i1, i2, j1, j2 in ops:
		if op == 'equal':
			out += a[i1:i2]
		elif op == 'insert':
			out += sgr(BG_GRN, BOLD)+(''.join(b[j1:j2]))+sgr()
		elif op == 'delete':
			out += sgr(BG_RED, BOLD)+(''.join(a[i1:i2]))+sgr()
	return (out, sm.ratio())

###############
## URL Utils ##
###############

ERR_BAD_URL = 'That URL didn\'t lead to a Sufficient Velocity or SpaceBattles post.'

# Matches yield three parameters, the thread ID, the page number (possibly None)
# and the post ID
THREAD_ID_REGEX = re.compile(\
	r"^https?://forum"+ \
	r"(?:s\.sufficientvelocity|s\.spacebattles|\.questionablequesting)\.com"+ \
	r"/threads/[A-Za-z0-9\-]*\.(\d*)/(?:page-(\d*))?#post-(\d*)$"\
)

def make_page_url(domain, thread, page):
	return \
		'http://'+domain+'/threads/.%d/page-%d' % (thread, page)

# returns a tuple (thread ID, page number, post ID) from a
# post URL. returns None if the post URL is not well formed.
def get_url_info(url):
	match = THREAD_ID_REGEX.match(url)
	if match == None:
		return None
	thread_id, page, post = match.groups()
	thread_id = int(thread_id)
	post = int(post)
	if page is not None:
		page = int(page)
	else:
		page = 1
	return (thread_id, page, post)

# gets the URL info, or dies if the URL doesn't parse
def get_url_info_or_die(url):
	info = get_url_info(url)
	if info is None:
		error(ERR_BAD_URL)
		exit(2)
	return info

#################
## Error Utils ##
#################

def warning(str):
	print '['+sgr(FG_YEL, BOLD, BLINK)+'!'+sgr()+'] '+sgr(FG_YEL, BOLD)+\
		'WARNING'+sgr()+': '+str

def acknowledge_warning(str):
	stdout.write('['+sgr(FG_RED, BOLD, BLINK)+'!'+sgr()+'] '+sgr(FG_RED, BOLD)+\
		'WARNING'+sgr()+': '+str+' (ENTER to continue)')
	raw_input()

def error(str):
	print '['+sgr(FG_RED, BOLD, BLINK)+'!'+sgr()+'] '+sgr(FG_RED, BOLD)+\
		'ERROR'+sgr()+': '+str
