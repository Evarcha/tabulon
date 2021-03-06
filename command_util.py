# Tabulon
# Copyright (c) 2015-2017 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

import re
from display import get_formatted_vote_line
from command_core import *
from setmath import setmath
import errstr

###################################
## Helper Functions for Commands ##
###################################

# sorted need not include all votes
def show_sorted_vote(mapping, sorted, replacement_texts=None, extra_texts=None):
  if replacement_texts is not None:
    assert len(replacement_texts) == len(sorted)
  if extra_texts is not None:
    assert len(extra_texts) == len(sorted)

  # invert the mapping so we have vote numbers
  inv_mapping = dict((mapping[i], i) for i in range(len(mapping)))

  for i in range(len(sorted)):
    vote = sorted[i]
    text = None
    extra = None
    if replacement_texts is not None:
      text = replacement_texts[i]
    if extra_texts is not None:
      extra = extra_texts[i]
    print(get_formatted_vote_line(vote, inv_mapping[vote], 0, text, extra))

def move(mapping, from_vote, to_vote):
  if from_vote == to_vote:
    raise CommandError(errstr.MOVE_TO_SELF)
  if mapping[to_vote].is_descendant_of(mapping[from_vote]):
    raise CommandError(errstr.MOVE_TO_DESCENDANT)
  mapping[to_vote].add(mapping[from_vote])

def multimerge(mapping, froms, tos):
  primary_to = tos[0]
  other_tos = tos[1:]

  # Validate first
  for from_vote in froms:
    for some_to in tos:
      if some_to==from_vote:
        raise CommandError(errstr.MERGE_TO_SELF)

    if mapping[primary_to].is_descendant_of(mapping[from_vote]):
      raise CommandError(errstr.MERGE_TO_DESCENDANT)

  # Now merge
  for from_vote in froms:
    for other_to in other_tos:
      mapping[other_to].copy(mapping[from_vote])

    mapping[primary_to].merge(mapping[from_vote])

# So this is a hideous-looking ball of regex, ain't it...
# Its purpose is to match to a find-replace regex in the form /find/replace/,
# allowing the forward slash to be escaped inside of the regex. Group one is
# find, and group two is replace.
FIND_REPLACE_REGEX = \
  re.compile(r"^/((?:[^/\\]|\\[^/]|\\/)*)/((?:[^/\\]|\\[^/]|\\/)*)/$")

# This returns all of the matched votes.
def find_replace_regex(regex, votes):
  match = FIND_REPLACE_REGEX.match(regex)
  if match is None:
    raise CommandError(errstr.FIND_REPLACE_BAD_FORMAT)
  search, replace = match.group(1, 2)

  try:
    compiled = re.compile(search)

    matched = []
    for vote in votes:
      s, n_matches = compiled.subn(replace, vote.primary_text)
      if n_matches > 0:
        vote.rename(s)
        matched.append(vote)
    return matched
  except re.error as e:
    raise CommandError(errstr.REGEX_ERROR, '('+str(e)+')')

# split_str is an array of strings
def parse_line_numbers(split_str, mapping, force_plural_error = False):
  try:
    out = [ int(i) for i in split_str ]
  except ValueError:
    if len(split_str) == 1 and not force_plural_error:
      raise CommandError(errstr.INVALID_INDEX)
    else:
      raise CommandError(errstr.INVALID_INDICES)

  for index in out:
    if index < 0 or index >= len(mapping):
      if len(split_str) == 1 and not force_plural_error:
        raise CommandError(errstr.INDEX_OUT_OF_RANGE)
      else:
        raise CommandError(errstr.INDICES_OUT_OF_RANGE)

  return out

def parse_line_number(str, mapping):
  try:
    out = int(str)
  except ValueError:
    raise CommandError(errstr.INVALID_INDEX)
  if out < 0 or out >= len(mapping):
    raise CommandError(errstr.INDEX_OUT_OF_RANGE)
  return out

def wait_for_line(str=None):
  out = '[ENTER] to continue'
  if str:
    out = str + ' ' + out
  input(out)

# Parses a list of line numbers in the form '1+2+c3+R6-c5'. The 'r' prefix means
# "this line, and all its kids recursively." The 'R' prefix is the same, but
# excludes the line itself. The 'c' prefix means "this line, and all its
# immediate children," and the 'C' prefix is the same excluding the line itself.
# The operator syntax is just regular setmath.
def parse_line_numbers_with_expands(str, mapping):
  def set_callback(type, digs):
    if type not in 'cCrR':
      return None

    vote = mapping[parse_line_number(digs, mapping)]
    out = set()

    if type in 'cC':
      out.update(vote.subs)
    elif type in 'rR':
      out.update(vote.recursive_children())

    if type in 'cr':
      out.add(vote)

    return out

  out = set()
  dels = set()

  return list(setmath(str, set_callback))
