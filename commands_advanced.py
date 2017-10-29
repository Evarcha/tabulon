# Tabulon
# Copyright (c) 2015-2017 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from command_core import *
from command_util import *
from util import *
import errstr
from setmath import setmath

#######################
## Advanced Commands ##
#######################

# All the advanced commands go in here. These are a little ill-defined, but
# generally if they're not porcelain around a few simple library commands
# they belong here.

TJ_TRANSLATE_REGEX = re.compile(r'[^A-Za-z]+')

class TypoJam(Command):
  def names(self):
    return ['typojam', 'tj']

  def go(self, args, model):
    mapping = model.mapping
    try:
      idx = int(args)
    except ValueError:
      raise CommandError(errstr.INVALID_INDEX)

    if idx<0 or idx >= len(mapping):
      raise CommandError(errstr.INVALID_INDEX)

    compare_raw = mapping[idx].primary_text
    compare_munge = self.translate(mapping[idx])

    matches = []
    munge_ratios = { compare_munge: 1.0 }
    raw_diffs = { compare_raw: (compare_raw, 1.0) }

    parents = []
    parent = mapping[idx].parent
    while parent != None:
      parents.append(parent)
      parent = parent.parent

    for i in range(len(mapping)):
      if i == idx:
        continue

      i_raw = mapping[i].primary_text
      i_munge = self.translate(mapping[i])

      if i_munge not in munge_ratios:
        munge_ratios[i_munge] = diff_strings(compare_munge, i_munge)[1]

      if i_raw not in raw_diffs:
        raw_diffs[i_raw] = diff_strings(compare_raw, i_raw)

      ratio = max(munge_ratios[i_munge], raw_diffs[i_raw][1])

      if ratio > 0.85:
        if mapping[i] in parents:
          warning('Parent #%d matched, ignoring' % i)
        else:
          matches.append((ratio, i, raw_diffs[i_raw][0]))

    matches.sort()
    matches.reverse()

    if len(matches) < 1:
        wait_for_line('No matches found.')
        return

    show_sorted_vote(
      mapping,
      [ mapping[i] for ratio, i, plain_diff in matches ],
      [ plain_diff for ratio, i, plain_diff in matches ],
      [ '(%4.1f%%)' % (100*ratio) for ratio, i, plain_diff in matches ],
    )

    remove = input(
      'Accept? (ENTER accepts all, none accepts none, or you can provide '+\
      'specific indices) '
    )
    if remove.strip().lower() == 'none':
      pass
    elif remove.strip() == '':
      for ratio, i, plain_diff in matches:
        mapping[idx].merge(mapping[i])
    else:
      ok_is = set([ i for ratio, i, plain_diff in matches ])

      if remove.find(',') == -1:
        remove = remove.split(' ')
      else:
        remove = remove.split(',')
      try:
        remove = [ int(a) for a in remove ]
      except ValueError:
        raise CommandError(errstr.INVALID_INDICES)
        return
      for value in remove:
        if value not in ok_is:
          warning('Couldn\'t resolve %d, not a found duplicate' % value)
        else:
          mapping[idx].merge(mapping[value])

  def translate(self, vote):
    t = vote.primary_text
    t.replace(' ', '')
    t = TJ_TRANSLATE_REGEX.sub('?', t)
    return t.strip('?')

  def description(self):
    return 'Try to find lines that are typos of a particular line, and help '+\
      'merge them together.'
  def usage(self):
    return ['typojam 1']


class SetMath(Command):
  def names(self):
    return ['setmath', 'sm']
  def go(self, args, model):
    def set_callback(type, digs):
      type = type.lower()
      if type not in 'vyn':
        return None

      digs = parse_line_number(digs, model.mapping)

      if type == 'v':
        return model.mapping[digs].yea | model.mapping[digs].nay
      elif type == 'y':
        return model.mapping[digs].yea
      elif type == 'n':
        return model.mapping[digs].nay

    result = setmath(args, set_callback)

    print(('Result (%d users): ' % len(result)) +', '.join(u for u in result))
    wait_for_line()

  def oper(self, left, oper, right):
    if oper == '&':
      return left & right
    elif oper == '+':
      return left | right
    elif oper == '-':
      return left - right
    else:
      assert False

  def description(self):
    return 'Calculate complex combinations of voters.'
  def usage(self):
    return ['setmath y1 - v2', 'setmath y1 & y2', 'setmath v0 - (n1 + n2 + n3)']
  def info(self):
    return """The setmath command performs basic set calculations on the sets
of people who voted for or against different vote options. For example, if you
want to find everybody who voted for line 1, but neither for or against line 2,
you can use the command 'setmath y1 - v2'.

Operands:
  y1: All of the users who voted 'Yea' to line 1.
  n1: All of the users who voted 'Nay' to line 1.
  v1: All of the users who voted (either way) on line 1.

Operators:
  & (AND): Find all of the users in both of the two operands.
  + (OR): Find all of the users in either of the two operands.
  - (Difference): Find all of the users in the first operand but not the second.

All of setmath's operators have the same precedence; they're evaluated from \
left to right."""

class RegexMoveRename(Command):
  def names(self):
    return ['moveregex', 'vr']
  def description(self):
    return 'Move and rename items according to a regex.'
  def usage(self):
    return [
      r"moveregex r0 1 /^Flee (east|west)!/Run \1!/",
      'moveregex R0-r26 27 '+\
        r"/Tay?lor's (?:cape )?name [sa]houl?d be ([^.]*)\.?/\1/"
    ]
  def go(self, args, model):
    slashpos = args.find('/')
    if slashpos < 0:
      raise CommandError(errstr.FIND_REPLACE_BAD_FORMAT)
    regex = args[slashpos:].strip()
    args = args[:slashpos]

    space_pos = args.strip().rfind(' ')
    if space_pos < 0:
      raise CommandError(errstr.TOO_FEW_ARGUMENTS)

    equation = args[:space_pos]
    dest_idx = parse_line_number(args[space_pos:], model.mapping)
    destination = model.mapping[dest_idx]

    froms = parse_line_numbers_with_expands(equation, model.mapping)
    initial_length = len(froms)
    froms = [x for x in froms if (not destination.is_descendant_of(x)) and x != destination]

    if initial_length > len(froms):
      warning( \
        '%d items removed for being ancestors of the destination. %d remain.'\
          % ( initial_length - len(froms), len(froms) )\
      )

    found = find_replace_regex(regex, froms)

    for vote in found:
      destination.add(vote)
  def info(self):
    return """The moveregex command finds all vote lines in the specified
search area that match a given regex. It renames them according to that regex,
and moves them to the desired destination.

The first argument to moveregex is an equation in setmath notation describing
which vote lines to search in the regex. The string 'r0' matches everything.
See the setmath documentation for more information on the format. Available
operands are r#, which matches recursively everything underneath the given node
number, R#, which is like r# but doesn't actually match the given node, c#,
which only matches the immediate children of the immediate node number, C#,
which is to c# as R# is to r#, and just a bare node number, which will match
only that node.

The second argument to moveregex is the line number of the node to move all of
the matches to.

The third argument to moveregex is the regex. This regex has two parts; it's
split like /find/replace/. Explaining regexes is outside of the scope of this
documentation, but you can find Python's documentation on regular expressions
at https://docs.python.org/2/library/re.html."""
