# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

###################
## Console Utils ##
###################

_is_ansi_enabled = True

def set_ansi_enabled(ansi):
	global _is_ansi_enabled
	_is_ansi_enabled = ansi

def is_ansi_enabled():
	global _is_ansi_enabled
	return _is_ansi_enabled

CSI = "\033["
BEL = "\007"

FG_BLK = FG_LBLK = '30'
FG_RED = FG_LRED = '31'
FG_GRN = FG_LGRN = '32'
FG_YEL = FG_LYEL = '33'
FG_BLU = FG_LBLU = '34'
FG_MGN = FG_LMGN = '35'
FG_CYN = FG_LCYN = '36'
FG_WHT = FG_LWHT = '37'

BG_BLK = BG_LBLK = '40'
BG_RED = BG_LRED = '41'
BG_GRN = BG_LGRN = '42'
BG_YEL = BG_LYEL = '43'
BG_BLU = BG_LBLU = '44'
BG_MGN = BG_LMGN = '45'
BG_CYN = BG_LCYN = '46'
BG_WHT = BG_LWHT = '47'

FG_HBLK = '30;90'
FG_HRED = '31;91'
FG_HGRN = '32;92'
FG_HYEL = '33;93'
FG_HBLU = '34;94'
FG_HMGN = '35;95'
FG_HCYN = '36;96'
FG_HWHT = '37;97'

BG_HBLK = '40;100'
BG_HRED = '41;101'
BG_HGRN = '42;102'
BG_HYEL = '43;103'
BG_HBLU = '44;104'
BG_HMGN = '45;105'
BG_HCYN = '46;106'
BG_HWHT = '47;107'


BLINK = '5'
BOLD = '1'
UNDERLINE = '4'
INVERSE = '7'

CLEAR_DISPLAY = CSI+'H'+CSI+'J'

def sgr(*args):
	if not is_ansi_enabled():
		return ''

	return CSI+(';'.join(args))+"m"

def pos(x, y):
	if not is_ansi_enabled():
		return ''

	return CSI+str(y+1)+';'+str(x+1)+'H'
