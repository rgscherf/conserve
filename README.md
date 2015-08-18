# Super Conservation Officer (SCO)

It needs a better name.

## Overview

SCO is a puzzle-y roguelike. You play as a conservation officer, trying to balance an ecosystem of AI animals. Each type of animal has different behaviors and a different place in the food web.

The design goal is that these variables will be interesting in their own right, as well as forming surprising tactical puzzles when they're combined in random ways.

SCO is my first game, so development will be really slow probably!

#### Notes for me

- Animals:
	- Pig: (DONE) moves to nearest body of water, then moves randomly. 
	- Wolf: finds nearest prey animal, and then heads right for it. Rests for 1 turn after eating an animal.
- Player: The player's job is to balance the ecosystem, not exterminate enemies. To that end, we need:
	- A scoring system that reflects "balance"
	- A toolkit for modifying/shaping the environment and AI behaviours.