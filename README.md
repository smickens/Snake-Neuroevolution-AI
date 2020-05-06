# Snake-Neuroevolution-AI

This program uses a genetic algorithm called NEAT (Neuroevolution of Augmenting Topologies) to teach a computer how to play the classic Snake game.

In each generation, it creates a population of 200 snakes. For each snake, the genetic algorithm takes in 10 inputs: x distance between snake head to food, y distance between snake head to food, and 8 inputs for what is around the snake head (snake body: -1, food: 1, wall: -1, or empty: 0). Based on these inputs, it calculates four outputs, and the greatest output determines what direction the snake moves. 

After each generation, it generates a new population based off the based snakes, the ones with the highest fitness scores, from the previous generation. Then, it repeats the process. 
