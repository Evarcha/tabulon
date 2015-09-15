# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from time import sleep, time
from sys import stdout
from collections import deque
from threading import Thread
from lxml import html
import requests
from util import *
from termutil import *
from getpass import getpass
import os, os.path

####################
## Fetching Utils ##
####################

_session = requests.Session()
_session.headers.update({'User-Agent': 'Tabulon/1.0'})

# Fetch this one uri
def single_fetch(uri):
	return html.fromstring(_session.get(uri).text)

# Fetch this one uri, returning the final uri after redirects
# Returns a tuple (lxml.html, uri)
def single_fetch_resolve_redirects(uri):
	response = _session.get(uri)
	return (html.fromstring(response.text), response.url)

def log_in_to_forum(scheme, host):
	print 'Trying to log in to '+host+'.'
	print

	while True:
		un = raw_input('Username: ')
		pw = getpass()
		print

		uri = scheme+'://'+host+'/login/login'

		response = _session.post(uri,
			data={
					'login': un,
					'password': pw,
					'register': '0',
					'remember': '1',
					'redirect': '/watched/threads',
					'_xfToken': '',
					'cookie_check': '0',
			},
		)

		if url_get_path(response.url) != '/watched/threads':
			print 'Oops, that didn\'t seem to work. Try again?'
			print
		else:
			break


def _multi_fetch_thread(uriq, out, print_progress):
	while True:
		try:
			uri = uriq.popleft()
		except IndexError:
			return
		out[uri] = single_fetch(uri)

def _multi_fetch_meter(n, fetched):
	start = time()
	while True:
		stdout.write(CSI+'0G')

		if n == len(fetched):
			break

		proportion = len(fetched) * 1.0 / n
		if proportion < 0.3:
			color = FG_RED
		elif proportion < 0.6:
			color = FG_YEL
		else:
			color = FG_GRN

		meter = sgr(color, BOLD)+('|'*len(fetched))+(' '*(n-len(fetched)))+sgr()
		progress = '(%2d / %2d)' % (len(fetched), n)

		stdout.write('Fetching: [%s] %s' % ( meter, progress ))

		stdout.write(CSI+'K')
		stdout.flush()

		last_done = len(fetched)
		while len(fetched) == last_done:
			sleep(0.025)

	print CSI+'0G'+('Done! (%d pages, %.1fsec)' % (n, time() - start))+CSI+'K'

# Fetch all the uris in the list, n at a time.
def multi_fetch(uris, n=6, use_meter=True):
	if not is_ansi_enabled():
		use_meter = False

	if len(uris) < 1:
		return []

	uriq = deque(uris)
	fetched = {}
	if n > len(uris):
		n = len(uris)
	threads = [
		Thread(target=_multi_fetch_thread, args=(uriq, fetched, not use_meter))
		for i in xrange(n)
	]
	if not use_meter:
		print 'Fetching', len(uris), 'pages...'
		start = time()
	for thread in threads:
		thread.start()
	if use_meter:
		meter = Thread(
			target=_multi_fetch_meter,
			args=(len(uris), fetched)
		)
		meter.start()
	for thread in threads:
		thread.join()
	if use_meter:
		meter.join()
	else:
		print 'Fetched', len(uris), 'pages in', ('%.1fsec' % (time() - start))
	return [ fetched[uri] for uri in uris ]
