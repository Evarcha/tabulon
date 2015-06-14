# Tabulon QM's Manual

## Overview

Tabulon is an alternative vote counting system for SV quests. It's built to have both a richer syntax for votes and more useful interpretation and analysis of the vote results.

Unlike other vote-counting systems you might have used, Tabulon is built around the interpretation of individual vote lines, arranged hierarchically as they are in their original votes.

Tabulon is a command-line application; it might be unfamiliar to you if you don't know much about the command line.

## Help System

Tabulon has a fully-functional help system. Just type `help` at the Tabulon prompt to see a full list of commands, including a few that weren't used in this tutorial. If you want more information on a specific command, typing `help [command name]` will tell you more.

## Tutorial

I'm going to go through my normal process for cleaning up a vote. Be sure to follow along with *all* the commands, in the order that I use them; otherwise, your line numbering will fall out of sync with mine, and then the tutorial will stop making sense.

Let's start by loading the vote from one of my quest's old updates, with

	python tabulon.py https://forums.sufficientvelocity.com/posts/3679259/ https://forums.sufficientvelocity.com/posts/3687873/

Gosh, this vote is a mess. I *could* post it like this, but neither I nor my players would be able to make heads or tails of this. That's why most of Tabulon's functionality is actually dedicated to cleaning up vote results, to make them easier to understand for everybody. Let's get going!

I did one interesting thing in this vote – I had a "half-update" in the middle of the vote. While that didn't affect the vote *much*, there was a decision that players were better-informed to make after reading the half-update. Because of this, I asked users to make votes after the half-update under a specific vote option. This is shown as option #6. Looks like the results are pretty unanimous: everyone wants to go away. But any option with enough votes will have typos, and I bet this one won't be an exception; let's clean this up with `typojam 6`. Looks like there *was* one – and `typojam` has just merged it into the main option with just the press of an enter key. (And now it's moved up to position #1!)

On the other hand, it looks like there are still typos nested inside that vote. Line #4 is exactly like line #5, except that one of them adds the word "Okay." That's cluttering up the results; as a rule, I like to merge substantially similar vote options. You could use `typojam` on this, but let's use the manual merge command this time: use `merge 4 5` if you prefer the "Okay," or `merge 5 4` if you don't.

Now, let's move on to the next top-level option, #6. As usual, it's got a typo version; `typojam 6` will clean that right up. It also has a typo suboption; `merge 9 8` fixes that.

There's one last typo, in this case because I changed the wording of a preset option after someone had already voted. (D'oh!) Option #28 is almost exactly like option #18. Observe, however, that `typojam 18` won't fix this - I added a whole new phrase to the vote, and that's made it too dissimilar for `typojam` to pick up on. Instead, use `merge 28 18` to clean it up.

There are also two vote options that are worded completely differently, but mean the same thing. The new #28 is basically equivalent to #14, assuming that this particular player doesn't plan to go all literal-genie on their promise not to interfere; merge the two of them together with `merge 28 14`.

One last thing: there's one vote line with only negative votes. I usually like to remove those before posting, because they aren't really conveying any information. Use `remove 17` to get rid of that line.

It looks like there aren't any more merges needed here; but, yikes, this is still a complicated vote! Let's try to simplify it a little bit; it would be nice to know how many of the people who want to be in on the counselor meeting haven't read the mini-update. Options #14 and #17 are asking to stay in on the meeting, and option #1 indicates that users have read the mini-update. To find out people who have picked both, you can use `setmath v1 & (v14 + v17)`. It turns out that there *are* two such people: StackedDeck and OverReactionGuy. It's not really a big deal to me, since there are only two of them, but if I wanted to look into it further, I could use `voteof StackedDeck` and `voteof OverReactionGuy` to show me their full votes.

There's also one more thing to check up on: line #22 is a really awful pun. Find out who inflicted it on the vote totals with `blame 22`. Looks like someone is living up to their name, haha...

This is about as good as it's going to get; I should now use the `bbcode` command to write the results out as BBCode, so I can copy-paste it into my update.

Once you're done with that, type `quit` to close Tabulon. Time to get writing!
