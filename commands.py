# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

# Commands List

from command_core import *
from command_util import *
from commands_arrange import *
from commands_info import *
from commands_advanced import *
from commands_undo import *

class Help(Command):
	show_unlisted = False
	def names(self):
		return ['help', '?']
	def description(self):
		return 'Helps you figure out how to use Tabulon.'
	def info(self):
		return 'If you pass help the name of another command, it\'ll provide '+\
			'information about that specific command. If you don\'t, it\'ll list '+\
			'all of the commands.'
	def usage(self):
		return ['help', 'help multimerge']
	def go(self, args, model):
		global COMMANDS, COMMAND_LIST
		args = args.strip().lower()

		if args:
			if args not in COMMANDS:
				print errstr.UNKNOWN_COMMAND
				print 'Use help to list all the known command names.'
			else:
				command = COMMANDS[args]
				names = command.names()
				print names[0]
				if len(names)>1:
					print 'aka '+(', '.join(names[1:]))
				print
				print command.description()
				print
				print 'usage:'
				for usage in command.usage():
					print '  '+usage
				info = command.info()
				if info is not None:
					print
					print info
				print
		else:
			print 'Tabulon Commands:'
			print
			for command in COMMAND_LIST:
				if command.unlisted() and not self.show_unlisted:
					continue

				names = command.names()

				out = '  '+names[0]
				if len(names) > 1:
					out += ' (aka '+(', '.join(names[1:]))+')'
				out += ': '+command.description()
				print out

			print
			print 'For more information on any particular command, call the help '+\
				'command with the name of the command as an argument. For example, '+\
				'"help multimerge."'
			print
		wait_for_line()

class UnlistedHelp(Help):
	show_unlisted = True
	def names(self):
		return ['uhelp', 'u?']
	def unlisted(self):
		return True
	def description(self):
		return 'Helps you figure out how to use Tabulon, including its unlisted '+\
			'commands.'

class Quit(Command):
	def names(self):
		return ['quit']
	def go(self, args, model):
		# pretend the user typed control-C
		raise KeyboardInterrupt()
	def description(self):
		return 'Close Tabulon.'
	def usage(self):
		return ['quit']

COMMAND_LIST = [
	Add(),
	Merge(),
	MultiMerge(),
	Invert(),
	Move(),
	Remove(),
	Rename(),
	MoveRename(),
	RegexMoveRename(),
	Trickle(),
	Recompute(),
	Blame(),
	Info(),
	VoteOf(),
	TypoJam(),
	SetMath(),
	BBCode(),
	Undo(),
	Redo(),
	Quit(),
	Help(),
	UnlistedHelp(),
]

def _generate_commands_array():
	global COMMANDS, COMMAND_LIST
	COMMANDS = {}
	for command in COMMAND_LIST:
		for name in command.names():
			name = name.lower()

			if name in COMMANDS:
				raise NameError('The name "'+name+'" is used by multiple commands!')
			COMMANDS[name] = command

_generate_commands_array()

def run_console_command(vote, undo_stack, mapping, command, v4u):
	global COMMANDS

	model = CommandModel(vote, mapping, v4u, undo_stack)

	space = command.find(' ')
	args = ''
	if space!=-1:
		args = command[space+1:]
		command = command[:space]
	command = command.lower()

	if command in COMMANDS:
		try:
			COMMANDS[command].go(args, model)
		except CommandError as e:
			print e
			wait_for_line()
	else:
		print errstr.UNKNOWN_COMMAND

	undo_stack.update()
	return model.vote
