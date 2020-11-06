## Code
* C++ file just run
```
g++ main.cpp -o out
./out
```
Works pretty much for windows and ubuntu (no c++11 or dependencies)

Works upto 4x4 unfortunately (but at least it's correct minimax not trap or random thing)

You need to wait 1 minute before it tells start the simulation.
## Game Rules / Self assumptions:

1- Adjacency is assumed to be diagonal + 4 main directions
2- Grid starts empty
3- Any cycle with positive area counts 
```
11.
1..
...
```
is considered a cycle of length 3

## What I applied?

* Minimax full tree depth (so only works on 4 * 4 max)
* DFS (tarjan-like) linear method for finding cycles (no CV :D)
* Because backtracking in python will take ages so I decided to use C++ (no GUI because it will make it complicated to install run .. etc)
* Overall complexity O(3^n) * R * C * hashmap
* Using masks that are number representations in base 3

## Some optimizations that I tried and weren't good:
* Exploring only up to limited depth from current state:
    * Now I believe this won't work because of the nature of the game. A friend suggested this idea (till a depth where number of options become reasonable) and then returning the move which would get the best score up to that depth. Because of the nature of the game, in order to make a difference in score you would need about 6 moves in order to make a difference in score, otherwise it would be the same score and basically random simulation. 

## Some optimizations which I believe work really well:

* Cutting isomorphic boards:
    * If you have an empty board and place a token anywhere in the middle. It doesn't matter wherever you place it as long as it's somewhere aroudn in the middle.
    * 2 boards which can get from each other by rotation or cropping and swapping regions should yield the same output exactly.
    * The challenge is finding a clever representation which shrinks the number of possible boards so it would be possible to generate all states for boards upto somethign 10*10. This would have been greate but unfortunately I couldn't come up with something even fairly working.



## Challenges:

* The game itself is very complicated. For example it's hard to identify what's a bad move because the drawbacks for a bad move are generally identified after several moves in the tree which makes such optimizations really hard

* Getting a heuristic for isomorphic boards is super challenging which is probably a work worth of being a project.

* Too much code (even without a GUI)


