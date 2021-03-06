# Tabulon
# Copyright (c) 2015-2017 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from sys import stdout
from time import sleep, time
import argparse, errstr
from string import digits

from util import *
from termutil import *
from fetch import single_fetch_resolve_redirects, multi_fetch, log_in_to_forum
from scrape import max_page_number_from_page, posts_from_page, \
  process_vote_from_posts, ParsedVote
from commands import run_console_command
from commands_undo import UndoStack
from vote import MergeableVote
from display import display_vote

import os, os.path, pickle, re

###############
## Core Loop ##
###############

MEMO_FILE_REGEX = re.compile(r'to_(\d+)\.memo')

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
    print('Tabulon')
  else:
    print('\033#3'+sgr(FG_HBLK)+'Tabulon\n\033#4'+sgr(FG_LWHT)+'Tabulon'+sgr())


  try:
    if not args.stop_uri:
      fetch_name = 'first page'
    else:
      fetch_name = 'start and stop pages'
    stdout.write('Fetching the '+fetch_name+'...')
    stdout.flush()
    start = time()
    start_page, start_uri = single_fetch_resolve_redirects(args.start_uri)

    dom = url_get_domain(start_uri)
    scheme = url_get_scheme(args.start_uri).lower()

    if scheme not in ['http', 'https']:
      error('Unknown connection scheme!')
      exit(1)

    if len(start_page.xpath('//div[@class=\'error_with_login\']')):
      # need to authenticate
      print()
      print()
      print('You might need to log in to see this thread.')

      if dom not in OK_FORUM_DOMAINS:
        error('Unknown domain for authentication!')
        exit(1)
      log_in_to_forum(scheme, dom)

      start = time()
      start_page, start_uri = single_fetch_resolve_redirects(args.start_uri)

    if args.stop_uri:
      stop_page, stop_uri = single_fetch_resolve_redirects(args.stop_uri)
    else:
      stop_page, stop_uri = None, None
    if args.disable_color:
      print()
      print('Fetched the '+fetch_name+' in '+('%.1fsec' % (time() - start)))
    else:
      print(CSI+'0GFetched the '+fetch_name+' in '+\
        ('%.1fsec' % (time() - start))+CSI+'K')
  except:
    print()
    error(errstr.COULDNT_FETCH_INITIAL)
    raise


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

  pages = [ start_page ] + multi_fetch( \
    [   \
      make_page_url(scheme, dom, threadno, i)     \
      for i in range(pageno+1, max_page+1)        \
    ]
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

  if not len(posts):
    error(errstr.NO_POSTS)
    exit(1)

  if not has_id:
    acknowledge_warning(errstr.COULDNT_FIND_NAMED_POST)

  # Load a memo file if possible (and the user wants that)
  memo_dir = os.path.expanduser(
    '~/.tabulon/'+dom.lower()+'/'+str(threadno)+'/'+str(postno)+'/'
  )

  memo_freeform = memo_mergeable = None

  if os.path.exists(memo_dir):
    # There could be applicable memo files!

    best = None

    for memo_file in os.listdir(memo_dir):
      match = MEMO_FILE_REGEX.match(memo_file)
      if match:
        last = int(match.group(1))
        if (best is None or last > best) and last <= posts[-1].id:
          # I think this generally makes sense, but it adds a weird situation
          # -- if the last vote gets deleted, we can't use the last memo.
          best = last

    if best and input('Load memo data? (Y/n) ').strip().lower() != 'n':
      best_path = memo_dir+'to_'+str(best)+'.memo'
      memo_mergeable, memo_freeform = pickle.load(open(best_path, 'rb'))

  v, parsed_votes, votes_for_user = \
    process_vote_from_posts(posts, memo_freeform, memo_mergeable)

  us = UndoStack(v)

  sleep(1)

  while True:
    try:
      if args.disable_color:
        print()
        print()
      else:
        print(CLEAR_DISPLAY)
      mapping = display_vote(v)
      print()
      command = input("> ").strip()

      v = run_console_command(v, us, mapping, command, votes_for_user)

      sleep(1)
    except KeyboardInterrupt:
      if input('Save memo data? (Y/n) ').strip().lower() != 'n':
        if not os.path.exists(memo_dir):
          os.makedirs(memo_dir)
        memo_file = memo_dir + 'to_'+str(posts[-1].id)+'.memo'
        us.teardown()
        pickle.dump((v, parsed_votes), open(memo_file, 'wb'), 1)
      break
