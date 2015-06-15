# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

from string import digits, ascii_letters
from command_core import CommandError
import errstr

def setmath(equation, set_callback):
	tokens = []
	i = 0
	while i < len(equation):	# gah, I want a real for loop
		c = equation[i]
		i+=1	# yuck, but this avoids bugs where I forget to i+=1...
		if c in ['(', ')', '+', '-', '&']:
			tokens.append((c, None))
		elif c in digits+ascii_letters:
			if c in digits:
				in_digits = True
				set_prefix = ''
				set_number = c
			else:
				in_digits = False
				set_prefix = c
				set_number = ''

			while i < len(equation) and equation[i] in digits+ascii_letters:
				if equation[i] in digits:
					in_digits = True
					set_number += equation[i]
				elif in_digits:
					raise CommandError(errstr.SETMATH_LEX)
				else:
					set_prefix += equation[i]
				i += 1

			if not in_digits:
				raise CommandError(errstr.SETMATH_LEX)

			set_value = set_callback(set_prefix, set_number)
			if set_value is None:
				raise CommandError(errstr.BAD_SET)

			tokens.append(('set', set_value))
		elif c in ' \t':
			continue
		else:
			raise CommandError(errstr.SETMATH_LEX)

	left_operands = [ None ]
	operators = [ None ]

	for token, selected in tokens:
		if token == '(':
			if left_operands[-1] is not None and operators[-1] is None:
				raise CommandError(errstr.SETMATH_PARSE, '(Open Parenthesis)')
			left_operands.append(None)
			operators.append(None)
		elif token == ')':
			if len(left_operands) == 1 or left_operands[-1] is None:
				raise CommandError(errstr.SETMATH_PARSE, '(Close Parenthesis)')
			if len(operators) == 1 or operators[-1] is not None:
				raise CommandError(errstr.SETMATH_PARSE, '(Close Parenthesis)')
			result = left_operands[-1]
			left_operands = left_operands[:-1]
			operators = operators[:-1]

			if operators[-1] is not None:
				left_operands[-1] = \
					_setmath_oper(left_operands[-1], operators[-1], result)
				operators[-1] = None
			else:
				left_operands[-1] = result
		elif token in ['+', '-', '&']:
			if left_operands[-1] is None:
				raise CommandError(errstr.SETMATH_PARSE, '(Operator)')
			operators[-1] = token
		elif token == 'set':
			if left_operands[-1] is None:
				left_operands[-1] = selected
			else:
				if operators[-1] is None:
					raise CommandError(errstr.SETMATH_PARSE, '(Set)')
				left_operands[-1] = \
					_setmath_oper(left_operands[-1], operators[-1], selected)
				operators[-1] = None

	if len(left_operands) != 1 or operators[-1] is not None:
		raise CommandError(errstr.SETMATH_PARSE, '(Exit)')

	return left_operands[-1]

def _setmath_oper(left, oper, right):
	if oper == '&':
		return left & right
	elif oper == '+':
		return left | right
	elif oper == '-':
		return left - right
	else:
		assert False
