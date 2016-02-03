# Super Conservation Officer (SCO)

It needs a better name.

## Overview

SCO is a puzzle-y roguelike. You play as a conservation officer, trying to balance an ecosystem of AI animals. Each type of animal has different behaviors and a different place in the food web.

The design goal is that these variables will be interesting in their own right, as well as forming surprising tactical puzzles when they're combined in random ways.

## Running

SCO requires [Kivy](http://www.kivy.org) and Python 2.7. Then:

`kivy src/game.py`

## How to play

WASD to move, IJKL to shoot a dart. Try to keep pigs, snakes and trees balanced for as long as possible!

## Rules

1. When a dart hits an object, it becomes a fence. No animal can cross a fence.

2. Pigs will move toward the nearest tree and eat it.

3. Snakes will pursue the nearest pig. When a snake eats a pig, it needs time to digest. The snake will start to hunt after it's finished digesting.

4. This is important: shooting a snake will move its head to the tile before the one you shot. Any segments of the snake's body between those two tiles turn into a tree.

## TODO?

More animal types.
