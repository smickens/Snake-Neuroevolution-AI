# Snake AI Using Genetic Algorithm called NEAT (Neuroevolution of Augmenting Topologies)
# Author: Shanti Mickens
# Date: April 14, 2020

import pygame
import random
import neat
import os

pygame.init()
pygame.display.set_caption("Snake")

# window size
WIN_WIDTH = 475
WIN_HEIGHT = 475
window = pygame.display.set_mode([WIN_WIDTH, WIN_HEIGHT])

# size of grid
GRID_WIDTH = 15
GRID_HEIGHT = 15

# stat font
highestScore = 0
generation = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont('comicsans', 28)

class Cell:
	SNAKE_COLOR = (150, 0, 0)
	FOOD_COLOR = (0, 120, 0)
	LIGHT_COLOR = (220, 220, 220)
	DARK_COLOR = (190, 190, 190)
	SIZE = 25

	def __init__(self, row, col, color):
		self.row = row
		self.col = col
		self.x = self.col*self.SIZE + 50
		self.y = self.row*self.SIZE + 50
		self.bgColor = color

	def draw(self, window):
		pygame.draw.rect(window, self.bgColor, (self.x, self.y, self.SIZE, self.SIZE))
# end of cell class
			
class Snake:
	VEL = 5

	def __init__(self):
		self.score = 0
		self.body = [[5, 4], [5, 3], [5, 2]]
		self.tick_count = 0 # keeps track of game clock, helps with physics of gravity
		self.direction = ""
		self.alive = True
		self.food = Food(self)

	def changeDir(self, d):
		# doesn't allow for snake to reverse direction
		if d == "up" and self.direction != "down":
			self.direction = d
		elif d == "right" and self.direction != "left":
			self.direction = d
		elif d == "down" and self.direction != "up":
			self.direction = d
		elif d == "left" and self.direction != "right":
			self.direction = d

	def isValid(self, i, j):
		# checks if snake went outside of grid boudnanries or if it ran into itself  
		if i < 0 or i > GRID_HEIGHT-1 or j < 0 or j > GRID_WIDTH-1:
			return False
		for s in range(len(self.body)):
			if self.body[s] == [i, j]:
				return False
		return True

	def checkIfEaten(self):
		# if food and part of snake body have same position, then snake ate the food
		if [self.food.row, self.food.col] in self.body:
			return True
		else:
			return False

	def grow(self, i, j):
		self.body.insert(-1, [i, j])

	def updateBody(self):
		# updates body position by having index 3 = index 2, index 2 = index 1, and so on
		for i in range(len(self.body)-1, 0, -1):
			self.body[i][0] = self.body[i-1][0]
			self.body[i][1] = self.body[i-1][1]

	def move(self):
		# moves head in current direction and updates body positions
		if self.direction == "up":
			if self.isValid(self.body[0][0]-1, self.body[0][1]):
				self.updateBody()
				self.body[0][0] -= 1
			else: 
				self.alive = False

		elif self.direction == "right":
			if self.isValid(self.body[0][0], self.body[0][1]+1):
				self.updateBody()
				self.body[0][1] += 1
			else:
				self.alive = False

		elif self.direction == "down": 
			if self.isValid(self.body[0][0]+1, self.body[0][1]):
				self.updateBody()
				self.body[0][0] += 1
			else:
				self.alive = False

		elif self.direction == "left": 
			if self.isValid(self.body[0][0], self.body[0][1]-1):
				self.updateBody()
				self.body[0][1] -= 1
			else:
				self.alive = False

	def getCellPos(self, pos):
		# gets corresponding x and y positions for given row and col
		i = pos[0]
		j = pos[1]
		return grid[i][j].x, grid[i][j].y

	def isAlive(self):
		return self.alive

	def draw(self, window):
		for b in self.body:
			x, y = self.getCellPos(b)
			pygame.draw.rect(window, Cell.SNAKE_COLOR, (x+2, y+2, Cell.SIZE-4, Cell.SIZE-4))
# end of snake class

class Food:
	COLOR = (0, 120, 0)

	def __init__(self, snake):
		# finds a random row and column that the snake is not in
		while True:
			self.row = random.randint(0, GRID_HEIGHT-1)
			self.col = random.randint(0, GRID_WIDTH-1)
			if not [self.row, self.col] in snake.body:
				break

	def getCellPos(self, pos):
		# gets corresponding x and y positions for given row and col
		i = pos[0]
		j = pos[1]
		return grid[i][j].x, grid[i][j].y

	def draw(self, window):
		x, y = self.getCellPos([self.row, self.col])
		pygame.draw.rect(window, Cell.FOOD_COLOR, (x+2, y+2, Cell.SIZE-4, Cell.SIZE-4))


# sets up background grid
alternate = True
grid = []
for i in range(GRID_HEIGHT):
	grid.append([])
	for j in range(GRID_WIDTH):
		if alternate:
			grid[i].append(Cell(i, j, Cell.LIGHT_COLOR))
			alternate = False
		else:
			grid[i].append(Cell(i, j, Cell.DARK_COLOR))
			alternate = True

numNoIncrease = 0
highestScoreInGeneration = 0

def draw_window(window, snakes, generation):
	global highestScore, highestScoreInGeneration

	# clears window
	window.fill((255, 255, 255))

	# draws background grid
	for i in range(len(grid)):
		for j in range(len(grid[0])):
			grid[i][j].draw(window)

	for s in snakes:
		# draws snake
		s.draw(window)
		# draws food
		s.food.draw(window)
		if s.score > highestScoreInGeneration:
			highestScoreInGeneration = s.score
		if s.score > highestScore:
			highestScore = s.score

	# draws stats (score and generation)
	text = STAT_FONT.render("Score: " + str(highestScoreInGeneration), 1, (0, 0, 0))
	window.blit(text, (10, 15))
	text = STAT_FONT.render("Gen: " + str(generation), 1, (0, 0, 0))
	window.blit(text, (10, 30))
	text = STAT_FONT.render("Highest Score: " + str(highestScore), 1, (0, 0, 0))
	window.blit(text, (10, 450))

	# refreshes display
	pygame.display.update()


# fitness functions for neat have to accept genomes and config
def fitness(genomes, config):
	global score, highestScoreInGeneration, generation, numNoIncrease
	generation += 1
	highestScoreInGeneration = 0
	numNoIncrease = 0

	nets = [] # keeps track of neural networks
	ge = [] # keeps track of genomes
	snakes = []

	# sets up snakes 
	for _, g in genomes: # needs underscore since genome is a tuple with genome_id and genome (1, genome)
		# sets up snake's neural network based on genome
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		g.fitness = 0
		ge.append(g)
		snakes.append(Snake())

	clock = pygame.time.Clock()
	tick_count = 0

	run = True
	while run:
		clock.tick(30)
		tick_count += 1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit() # quit pygame
				quit() # quit program
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					# sets all living snakes fitnesses to 0
					for x, snake in enumerate(snakes):
						# removes snake from array
						ge[x].fitness = 0
						snakes.pop(x)
						nets.pop(x)
						ge.pop(x)
					print("end")
					run = False

		if len(snakes) == 0:
			# no snakes left, end generation
			run = False

		snakeAte = False
		for x, snake in enumerate(snakes):
			snake.move()

			# checks if snake is alive
			if snake.isAlive():
				# increases snake's fitness for still being alive
				ge[x].fitness += 0.1

				# checks if food was eaten
				if snake.checkIfEaten():
					# increases snake's fitness
					ge[x].fitness += 1.0
					# adds to score
					snake.score += 1
					# adds to snake body
					snake.grow(snake.food.row, snake.food.col)
					# creates new food
					snake.food = Food(snake)
					snakeAte = True

				# INPUTS
				# 1) x displacement to food
				xDis_food = snake.food.row-snake.body[0][0]
				# 2) y displacement to food ()
				yDis_food = snake.food.col-snake.body[0][1]

				# gets what is around snake head (snake body = -1, food = +1, wall = -1, or nothing = 0)
				headRow = snake.body[0][0];
				headCol = snake.body[0][1];

				upLeft = -1 if [headRow-1, headCol-1] in snake.body else 1 if [headRow-1, headCol-1] == [snake.food.row, snake.food.col] else -1 if headCol-1 < 0 or headRow-1 < 0 else 0;
				upMid = -1 if [headRow-1, headCol] in snake.body else 1 if [headRow-1, headCol] == [snake.food.row, snake.food.col] else -1 if headRow-1 < 0 else 0;
				upRight = -1 if [headRow-1, headCol+1] in snake.body else 1 if [headRow-1, headCol+1] == [snake.food.row, snake.food.col] else -1 if headCol+1 >= GRID_WIDTH or headRow-1 < 0 else 0;
				midLeft = -1 if [headRow, headCol-1] in snake.body else 1 if [headRow, headCol-1] == [snake.food.row, snake.food.col] else -1 if headCol-1 < 0 else 0;
				midRight = -1 if [headRow, headCol+1] in snake.body else 1 if [headRow, headCol+1] == [snake.food.row, snake.food.col] else -1 if headCol+1 >= GRID_WIDTH else 0;
				downLeft = -1 if [headRow+1, headCol-1] in snake.body else 1 if [headRow+1, headCol-1] == [snake.food.row, snake.food.col] else -1 if headCol-1 < 0 or headRow+1 >= GRID_HEIGHT else 0;
				downMid = -1 if [headRow+1, headCol] in snake.body else 1 if [headRow+1, headCol] == [snake.food.row, snake.food.col] else -1 if headRow+1 >= GRID_HEIGHT else 0;
				downRight = -1 if [headRow+1, headCol-1] in snake.body else 1 if [headRow+1, headCol-1] == [snake.food.row, snake.food.col] else -1 if headCol+1 >= GRID_WIDTH or headRow+1 >= GRID_HEIGHT else 0;

				# passes inputs to snake's neural network to decide what direction to go
				outputs = nets[x].activate((xDis_food, yDis_food, upLeft, upMid, upRight, midLeft, midRight, downLeft, downMid, downRight))

				# decides what direction to go
				if max(outputs) == outputs[0]:
					snake.changeDir("up")
				elif max(outputs) == outputs[1]:
					snake.changeDir("right")
				elif max(outputs) == outputs[2]:
					snake.changeDir("down")
				elif max(outputs) == outputs[3]:
					snake.changeDir("left")
			else: 
				# removes snake from array
				ge[x].fitness -= 1
				snakes.pop(x)
				nets.pop(x)
				ge.pop(x)

		if not snakeAte:
			# if no snake ate then it increments numNoIncrease, which represents the number of moves where no snake on board ate any food
			numNoIncrease += 1

		# breaks out of while loop if snake is going in a circle
		if numNoIncrease == 100:
			# sets all living snakes fitnesses to 0
			for x, snake in enumerate(snakes):
				# removes snake from array
				ge[x].fitness -= 1
				snakes.pop(x)
				nets.pop(x)
				ge.pop(x)
			break

		# breaks out of while loop if snake gets score of 50 since it probably won't ever lose
		for s in snakes:
			if s.score > 50:
				break

		# draws everything
		draw_window(window, snakes, generation)

# NEAT Algorithm Info
	# inputs = snake head to food row distance, snake head to food col distance, and 8 inputs for what is around the snake head
	# outputs = up, right, down , left
	# activation function = tanh (maps value between -1 to 1)
	# population size = 200 
	# fitness function = fitness plus 0.1 for every frame it is alive and plus 1 when it reaches food
	# max generations = 100

def run(config_path):
	# loads in configuration file and tells neat what headings we used in it
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	# creates population
	p = neat.Population(config)

	# gets stats
	p.add_reporter(neat.StdOutReporter(True))
	p.add_reporter(neat.StatisticsReporter())

	# sets fitness function
	winner = p.run(fitness, 100)


if __name__ == "__main__":
	# gets absolute path to config file
	local_dir = os.path.dirname(__file__) # gets path to current file
	config_path = os.path.join(local_dir, "config-feedForward.txt")
	run(config_path)




