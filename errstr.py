# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

# Errors

ADD_NEEDS_TEXT = 'You need to provide the text for your new vote option.'
RENAME_NEEDS_TEXT = 'You need to provide new text for this vote option.'
TOO_FEW_ARGUMENTS = 'You passed too few arguments into this command.'
TOO_MANY_ARGUMENTS = 'You passed too many arguments into this command.'
MERGE_TO_SELF = 'You can\'t merge a line with itself.'
MERGE_TO_DESCENDANT = 'You can\'t merge a line with its own descendant.'
MOVE_TO_SELF = 'You can\'t move a line to itself.'
MOVE_TO_DESCENDANT = 'You can\'t move a line under its own descendant.'
INVALID_INDEX = 'That wasn\'t a valid line number.'
INDEX_OUT_OF_RANGE = 'That line number is out of range.'
INVALID_INDICES = 'One of those line numbers wasn\'t valid.'
INDICES_OUT_OF_RANGE = 'One of those line numbers is out of range.'
UNKNOWN_COMMAND = 'Command unknown. Type ? to list commands.'
COULDNT_FETCH_INITIAL = 'Couldn\'t fetch the given URL.'
COULDNT_FIND_NAMED_POST = 'Couldn\'t find the post whose ID you referred to.'
SETMATH_LEX = 'There were unexpected characters in that equation.'
SETMATH_PARSE = 'That equation didn\'t make any sense.'
UNKNOWN_USER = 'I don\'t know who that user is.'
MULTIMERGE_NEEDS_ARROW = 'Separate the from posts and the to posts in a multimerge using an >.'
START_STOP_DOMAIN_MISMATCH = 'Your start and stop URIs are on different web sites.'
START_STOP_THREAD_MISMATCH = 'Your start and stop posts are in different threads.'
STOP_BEFORE_START = 'Your stop post is before your start post.'
FIND_REPLACE_BAD_FORMAT = 'That regex wasn\'t in the right format for Find/Replace. Try something like /find/replace/.'
TOO_MANY_PREFIXES = 'There are too many prefixes on one of those line numbers.'
REGEX_ERROR = 'That regular expression was badly formatted.'
BAD_SET = 'That wasn\'t a valid set name for this command.'
