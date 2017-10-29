# Tabulon

Tabulon is a system for managing votes in Sufficient Velocity and SpaceBattles quests. It is written in Python 2, and requires the `lxml` and `requests` libraries to be installed. The `pyperclip` module is optional, but will enable clipboard functionality. Tabulon was written for my [*Camp Cauldron Lake*](http://forums.sufficientvelocity.com/threads/camp-cauldron-lake-worm.18602/) quest on Sufficient Velocity.

Tabulon "thinks" somewhat differently from SV's other vote counters. Where they seem optimized for bandwagons, to pick the most-liked vote in its entirety, Tabulon prefers to synthesize, to surface the most-liked individual options and allow the QM to gather those into a coherent course of action.

Tabulon is a command-line application; it might be unfamiliar to you if you don't know much about the command line.

## Running Tabulon

	python tabulon.py start-uri [stop-uri]

Runs Tabulon. `start-uri` is the URI of the QM post (usually a story update) you'd like to start processing votes at. `stop-uri` is the URI of the post (usually a subsequent story update) that you'd like to stop processing votes at, and is optional.

### Example

	python tabulon.py https://forums.sufficientvelocity.com/posts/3679259/ https://forums.sufficientvelocity.com/posts/3687873/

This will show you the voting for the fifth chapter of "The Beautiful Ones" in my quest, *Camp Cauldron Lake*. It's a very messy vote, with lots of suggested options, plus duplicates and typos and such. If you want to practice cleaning up a vote, this would be a good choice; I walk you through doing it in the tutorial.

### Options

	--disable-color
	-w

Disables ANSI escape sequences, most notably for color, but also for clearing the screen after commands. While ANSI escape sequences are commonly supported, not all terminals handle them; most notably, the standard Windows console does not. If you see garbage characters in the terminal, but no color, you should probably turn this on.

## How to Use

See `PLAYERS.md` for instructions on how players can vote, and `QM.md` for instructions on how QMs can use the tool.

## Contributing

Send me a pull request! Several people expressed interest in the thread; if anyone still wants to help out, I have a list of things that would be useful (and that I don't want to do myself) in `FIXME.md`. Most of the things I think would be important need to wait until after I've finished implementing the extended command-line interface, though; the file's a little bare for now.

Regarding code style:
 * Use the logical tab (\t) character for indentation, not spaces.
 * Lines should not exceed 80 characters when viewed using two-space tabs.

## Authors

 * BeaconHill ([SB](https://forums.spacebattles.com/members/beaconhill.295356/), [SV](http://forums.sufficientvelocity.com/members/beaconhill.207/)). You'll hear back from me soonest if you contact me via PM on either forum.

## License

See the `LICENSE.txt` file for license terms.

(For anyone who cares about this sort of thing, Tabulon uses the ISC license, a permissive open-source license like the MIT or BSD licenses but less wordy.)

## Miscellaneous Tools

promptdb.py: Allows for ranked storage of writing prompts. I never felt like the ranking worked quite right...

## Disclaimer

I am providing code in this repository to you under an open source license. Because this is my personal repository, the license you receive to my code is from me and not from my employer.
