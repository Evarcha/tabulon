# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from sys import stdout
from time import sleep, time
import argparse, errstr
from string import digits

from util import *
from termutil import *
from fetch import single_fetch_resolve_redirects, multi_fetch
from scrape import max_page_number_from_page, posts_from_page, process_vote_from_posts
from commands import run_console_command
from display import display_vote

###############
## Core Loop ##
###############

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process quest votes on SB/SV.')
	parser.add_argument(
		'start_uri',
		help='The URI of the QM post you want to start from.',
	)
	parser.add_argument(
		'stop_uri',
		nargs='?',
		help='The URI of the QM post you want to stop at.'
	)
	parser.add_argument(
		'-w',
		'--disable-color',
		help='Disable terminal effects, like color.',
		action='store_true',
	)
	args = parser.parse_args()

	set_ansi_enabled(not args.disable_color)

	if args.disable_color:
		print 'Tabulon'
	else:
		print '\033#3'+sgr(FG_HBLK)+'Tabulon\n\033#4'+sgr(FG_LWHT)+'Tabulon'+sgr()

	try:
		if not args.stop_uri:
			fetch_name = 'first page'
		else:
			fetch_name = 'start and stop pages'
		stdout.write('Fetching the '+fetch_name+'...')
		stdout.flush()
		start = time()
		start_page, start_uri = single_fetch_resolve_redirects(args.start_uri)
		if args.stop_uri:
			stop_page, stop_uri = single_fetch_resolve_redirects(args.stop_uri)
		else:
			stop_page, stop_uri = None, None
		if args.disable_color:
			print
			print 'Fetched the '+fetch_name+' in '+('%.1fsec' % (time() - start))
		else:
			print CSI+'0GFetched the '+fetch_name+' in '+\
				('%.1fsec' % (time() - start))+CSI+'K'
	except:
		print
		error(errstr.COULDNT_FETCH_INITIAL)
		raise

	dom = url_get_domain(start_uri)

	if stop_uri and url_get_domain(stop_uri) != dom:
		error(errstr.START_STOP_DOMAIN_MISMATCH)
		exit(1)

	threadno, pageno, postno = get_url_info_or_die(start_uri)

	if not stop_uri:
		max_page = max_page_number_from_page(start_page)
		max_post = None
	else:
		stop_threadno, stop_pageno, stop_postno = get_url_info_or_die(stop_uri)
		if stop_threadno != threadno:
			error(errstr.START_STOP_THREAD_MISMATCH)
			exit(1)
		if stop_pageno < pageno or stop_postno < postno:
			error(errstr.STOP_BEFORE_START)
			exit(1)
		max_page = stop_pageno-1
		max_post = stop_postno

	pages = [ start_page ] + multi_fetch(	\
		[make_page_url(dom, threadno, i) for i in xrange(pageno+1, max_page+1)] \
	)

	if stop_page is not None:
		pages.append(stop_page)

	posts = []

	qm = None

	has_id = False
	for page in pages:
		new_posts = posts_from_page(page)
		for post in new_posts:
			if post.id == postno:
				has_id = True
				qm = post.author
			elif max_post is not None and post.id >= max_post:
				break
			elif post.id > postno and (qm is None or post.author != qm):
				posts.append(post)

	if not has_id:
		acknowledge_warning(errstr.COULDNT_FIND_NAMED_POST)

	v, votes_for_user = process_vote_from_posts(posts)

	sleep(1)

	while True:
		if args.disable_color:
			print
			print
		else:
			print CLEAR_DISPLAY
		mapping = display_vote(v)
		print
		command = raw_input("> ").strip()

		run_console_command(v, mapping, command, votes_for_user)

		sleep(1)
