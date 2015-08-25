# Super Conservation Officer (SCO)

It needs a better name.

## Overview

SCO is a puzzle-y roguelike. You play as a conservation officer, trying to balance an ecosystem of AI animals. Each type of animal has different behaviors and a different place in the food web.

The design goal is that these variables will be interesting in their own right, as well as forming surprising tactical puzzles when they're combined in random ways.

SCO is my first game, so development will be really slow probably!

## Ecology

You must tend to the food web, keeping the populations of various animal species in balance. Each species has a small set of behaviors:

#### Pig

Pigs eat trees. However, they will rush toward bird poop and eat it, which allows them to breed (when adjacent to another pig).

Pigs cannot cross player-made fences.

#### Eagle

Eagles eat pigs. Every time an eagle departs from the nest to hunt, it will leave behind an egg. The eagle will pick up the nearest pig and bring it back to the nest. If there is an egg in the nest, a new eagle will be born. The pig will die in either case. New eagles will fly a short distance before making a nest and beginning to hunt. 

Eagles can cross player-made fences (because they fly!) 

Shooting an eagle in flight will make it poop (and drop the pig it's carrying, if it has one). 

#### Muskrat

Muskrats eat eagle eggs. When it sees an eagle egg, the muskrat will grab it and bring the egg to the nearest body of water. When it reaches the water, a new muskrat will be born ON EVERY CLEAR TILE ADJACENT TO THE WATER.

Muskrats cannot cross player-made fences.

#### Snake

Snakes eat muskrats. The snake stretches its body from its starting position (a cave) toward the muskrat. If it reaches the muskrat, the snake swallows it and the muskrat is passed through the snake's body at a certain speed (ie X tiles per turn). If it reaches the end of the snake's body, a new snake is born. New snakes nest in an empty cave, then begin to hunt.

Snakes cannot cross player-made fences. 

Shooting a snake will turn every tile of its body (bewteen the impacted tile and the snake's head) into a tree. The body segment farthest from the snake's tail becomes the snake's new head.