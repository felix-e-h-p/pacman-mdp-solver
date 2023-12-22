
"""
Markov Decision Process (MDP) based agent representative of decision making processes in Pacman to win the game successfully

Respective Classes stated:

- MDPAgent: State based action decisions implemented, hyperparameters defined here
- MDPSolver: MDP Solver utilising the value iteration algorithm, optimal utility defined
- RewardFunction: Agent reward function relating to grid elements
- Grid: Modified and refined from practical 5
- Map: Modified and refined from practical 5
"""

# Standard module imports as follows
from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys

# Vector addition function specification
def add(vec1, vec2):
    return tuple([vec1[0] + vec2[0], vec1[1] + vec2[1]])

# Initialising and defining the MDPAgent Class
class MDPAgent(Agent):

    def __init__(self):
        print "Starting up MDPAgent!"
        self.name = "Pacman"
        self.map = Map()

    # Run after MDPAgent is created
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.map.registerInitialState(state)

    # Ran between multiple -n specified games
    def final(self, state):
        print "Looks like the game just ended!"

    # Value iteration function definition which then sequentially computes optimal policy
    def getAction(self, state):
        # Updates map with the current state
        self.map.updateFoodInMap(state)
        self.map.updateGhostsInMap(state)

        # Obtain legal actions for current state
        legal = api.legalActions(state)
        legal.remove(Directions.STOP)

        # Obtain states from map
        states = self.map.getStates()

        # Hyperparamaters for mediumClassic
        if len(states) == 106:
            gamma = 0.7
            movCost = 0.11
            perimeter = 4

        # Hyperparamaters for smallGrid
        elif len(states) == 18:
            gamma = 0.7
            movCost = 0.07
            perimeter = 1

        # Calculation of rewards via the RewardFunction    
        rewards = RewardFunction.reward(state, states, movCost, perimeter)
        actions = (Directions.SOUTH, Directions.NORTH, Directions.WEST, Directions.EAST)

        # Value iteration implementation via MDPSolver call
        utils = MDPSolver(actions, gamma, rewards).valueIteration()
        pos = api.whereAmI(state)
        choice = (Directions.STOP, -100)

        # Hence best possible action based on optimal utility value
        for action in legal:
            new_state = add(pos, game.Actions.directionToVector(action))
            if new_state in utils and utils[new_state] > choice[1]:
                choice = (action, utils[new_state])

        # Returns move choice based on percieved optimal utility
        return api.makeMove(choice[0], legal)

# Initialising and defining the MDPSolver Class
class MDPSolver:

    # Initialised utilities are at zero value
    def __init__(self, actions, gamma, rewards):
        """
        Parameters specified as:
        Actions - Tuple of possible actions of agent
        Gamma - Specified discount factor
        Rewards - Dictionary of states mapped to rewards
        """
        self.actions = actions
        self.gamma = gamma
        self.map_states_rewards = rewards
        self.map_states_utilities = {}
        for key in self.map_states_rewards.keys():
            self.map_states_utilities[key] = 0

    # Definition of the value iteration algorithm as function       
    def valueIteration(self):
        """
        Value iteration commences until convergance occurs
        Final converged utility values are returned
        Sum of state specific utility to check stabilisation
        """
        while(1==1):
            new_states = {}
            for state in self.map_states_utilities:
                new_states[state] = self.utilityOfState(state)
            if round(sum(self.map_states_utilities.values()), 2) == round(sum(new_states.values()), 2):
                return new_states
            self.map_states_utilities = new_states

    # Definition of the utility of state function
    def utilityOfState(self, state):
        """
        Utility of state based on utility of all subsequent potential states
        Fundamental implimentation of the Bellman update as stage process
        Reward based on current state and discounted expected utility utilised
        """
        if abs(self.map_states_rewards[state]) >= 1:
            return self.map_states_rewards[state]
        next_utils = []

        for action in self.actions:
            next_utils.append(self.expectedUtility(state, action))
        return self.map_states_rewards[state] + self.gamma * max(next_utils)

    # Returns expected utilities for potential next state    
    def expectedUtility(self, state, action):
        intended = add(state, game.Actions.directionToVector(action))
        intended = 0.8 * self.getLegalUtil(intended, state)

        # Computes expected utility for specified state and action
        if action is Directions.NORTH or Directions.SOUTH:
            left = add(state, game.Actions.directionToVector(Directions.WEST))
            right = add(state, game.Actions.directionToVector(Directions.EAST))
        else:
            left = add(state, game.Actions.directionToVector(Directions.NORTH))
            right = add(state, game.Actions.directionToVector(Directions.SOUTH))

        # For all potential specified and hence intended action values
        left = 0.1 * self.getLegalUtil(left, state)
        right = 0.1 * self.getLegalUtil(right, state)
        return intended + left + right

    # Formal definition of legally permissable utilities
    def getLegalUtil(self, next, current):
        return self.map_states_utilities[next] if next in self.map_states_utilities else self.map_states_utilities[current]

# Reward function Class which returns dictionary of rewards
# Utilises states as directly defined in getAction
# Dynamic positional elements of grid are paramount
class RewardFunction:

    @staticmethod
    def reward(state, paths, movCost, perimeter):
        """
        Parameters specified as:
        State - Current specified agent state
        Paths - List of certain available grid points
        movCost - Cost of movement relative to points
        Perimeter - Distance of ghost as obstruction for rewards
        """
        rewards = {}

        # movCost specifically defining penalty for agent food avoidance
        for point in paths:
            rewards[point] = -movCost
            if point in api.food(state):
                rewards[point] = 1/float(len(api.food(state)))

        # perimeter encouraging agent ghost avoidance
        for point in paths:
            if (point,  0) in api.ghostStates(state):
                for tile in paths:
                    distance = util.manhattanDistance(tile, point)
                    if distance <= perimeter:
                        rewards[tile] = -1/float(distance+1)
        return rewards

# Grid constructor Class - modified from lab session (practical 5)
class Grid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)
        self.grid = subgrid

    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                print self.grid[i][j],
            print 
        print

    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                print self.grid[self.height - (i + 1)][j],
            print 
        print

    def setValue(self, x, y, value):
        self.grid[int(y)][int(x)] = value

    def getValue(self, x, y):
        return self.grid[int(y)][int(x)]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

# Map constructor Class - modified from lab session (practical 5)
class Map:

    def __init__(self):
        print "Running init!"
        self.map = []

    def registerInitialState(self, state):
        print "Running registerInitialState!"
        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.updateGhostsInMap(state)
        self.map.display()

    def final(self, state):
        print "Looks like I just died!"

    def makeMap(self, state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    def updateFoodInMap(self, state):
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def updateGhostsInMap(self, state):
        ghosts = api.ghosts(state)
        for i in range(len(ghosts)):
            self.map.setValue(ghosts[i][0], ghosts[i][1], '@')

    # List of valid paths in specified map are returned
    def getStates(self):
        paths = []

        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    paths.append((i, j))
        return paths
