# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

############################
## Clipboard Shim Library ##
############################

# This is intended to detect when no clipboard library is installed, and quietly
# intercept calls. It will also eventually connect to multiple clipboard
# backends.

from util import acknowledge_warning
import errstr

has_pyperclip = True

try:
	import pyperclip
except ImportError:
	has_pyperclip = False

def copy(string):
	if has_pyperclip:
		pyperclip.copy(string)
	else:
		acknowledge_warning(errstr.NO_CLIPBOARD)

def paste():
	if has_pyperclip:
		return pyperclip.paste()
	else:
		acknowledge_warning(errstr.NO_CLIPBOARD)
		return ''

def available():
	return has_pyperclip
