"""
TITLE:          project.py
DIRECTORY:      Reinforcement Racer project.
DESCRIPTION:    Main project file for the reinforcement
                racer project - one of two primary projects
                for DU's ACS 2500: Core Apps of AI course.
MUTABILITY:     This file contains challenges that must be
                resolved for full project completion. (NOTE:
                You may answer relevant TODOs by creating
                additional docstrings and commented segments
                that contain your respective answers.)
"""


# Relative Imports and Instantiations
import numpy as np
import matplotlib.pyplot as plt
import os, sys, math, random
import neat, pygame

from structures.structures import CarAgent


# Setup Agent Variables
AGENT_PARAMETERS = {
    "X": 60, 
    "Y": 60
}

# Setup Game Environment Variables
ENVIRONMENT_PARAMETERS = {
    "WIDTH":    1920,
    "HEIGHT":   1080
}

# Set Color of Racetrack Border for Collision Detection
BORDER_COLOR = (255, 255, 255, 255)

# Set Flag for Tracking Generational Training
current_generation = 0


def racecar_simulator(genomes, configurations):
    """ Custom function to conduct simulated reinforcement learning using naive self-driving car object. """
    # Initialize arrays for storing models and game agent over training
    models, agents = list(), list()

    # Initialize PyGame utilities for training
    pygame.init(); screen = pygame.display.set_mode((ENVIRONMENT_PARAMETERS["WIDTH"], ENVIRONMENT_PARAMETERS["HEIGHT"]))
    
    # Iteratively train agent using Deep RL
    for iteration, genome in genomes:
        # TODO: What type of neural network is designed here? 
        # TODO: Can we utilize more advanced neural networks instead?
        # TODO: What is the tradeoff of using higher-order and/or lower-order networks? 
        """
        This project uses a Feedforward Neural Network.  It only sends information forward 
        to the following nodes, and does not create cycles or loops between the input and
        output layers.  It's a simple network that is easy to implement, but has a tradeoff
        of overfitting to the training set which could reduce the model's useability in
        other applications.  We could use a Deep Q-Learning network which uses the 
        state-action value function to approximate optimal Q values that allow the model
        to select ideal actions based on state data.  We could also implement experience 
        replay by reintroducing random samples of past data which would allow for better
        data efficiency and better stability with uncorrelated transitions.
        """
        model = neat.nn.FeedForwardNetwork.create(genome, configurations)
        
        # Save instantiated models with (re)set genetic training counter
        models.append(model)
        genome.fitness = 0

        # Instantiate agent with necessary state data
        agents.append(CarAgent(agent_parameters=AGENT_PARAMETERS,
                               environment_parameters=ENVIRONMENT_PARAMETERS,
                               border_color=BORDER_COLOR))

    # Create necessary parameters to set up PyGame environment for training
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)

    # Read in environment image map
    environment = pygame.image.load("assets/environments/custommap.png").convert()

    # Iterate generation counter as global variable 
    global current_generation
    current_generation += 1

    # Create dummy counter for early stopping
    counter = 0

    # Optimize agent driving directionality/velocity choices using game agent policy optimization
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        for iteration, agent in enumerate(agents):
            output = models[iteration].activate(agent.get_actions())
            choice = output.index(max(output))
            # TODO: Explain how policy selection works here – how are choices selected
            #       across our reinforcement learning agent? What do those choices
            #       actually do for our game-playing bot? 
            """
            We're using the values generated from the activate function of the 
            FeedForwardNetwork using the actions from CarAgent.get_actions() as our
            input.  We're then using the index of the max output to select a choice
            from the listings below.  The actions are computed using the distance values
            from the radars on the car that sense where the car is in relation the the boundaries.
            The choices either change the angle of the car, or increase/decrease the car speed.
            """
            if choice == 0:
                agent.angle += 10
            elif choice == 1:
                agent.angle -= 10
            elif choice == 2:
                if agent.speed - 2 >= 12:
                    agent.speed -= 2
            else:
                agent.speed += 2

        # Check if RL Agent is alive and optimize rewarding schema
        # TODO: Explain how the rewards are selected here – how is the 
        #       rewarding schema related to the model's training fitness?
        """
        Rewards are selected if the car is still alive, and they are based on
        the distance the car has traveled.  The model's fitness function is set
        to max stagnation, so a higher fitness indicates more desirable traits.
        """
        still_alive = 0
        for iteration, agent in enumerate(agents):
            if agent.is_alive():
                still_alive += 1
                agent.play_game(environment)
                genomes[iteration][1].fitness += agent.get_rewards()

        # Escape case if agent dies
        if still_alive == 0:
            break

        # Escape case after sufficient training generations
        counter += 1
        if counter == 30 * 40:
            break

        # Update screen rendition
        screen.blit(environment, (0, 0))
        for agent in agents:
            if agent.is_alive():
                agent.draw(screen)

        # Render additional visual information for RL task
        text = generation_font.render("Generation: {}".format(str(current_generation)),
                                      True,
                                      (0, 0, 0))
        text_rectangle = text.get_rect()
        text_rectangle.center = (900, 450)
        screen.blit(text, text_rectangle)

        text = alive_font.render("Still Alive: {}".format(str(still_alive)),
                                 True,
                                 (0, 0, 0))
        text_rectangle = text.get_rect()
        text_rectangle.center = (900, 490)
        screen.blit(text, text_rectangle)

        pygame.display.flip(); clock.tick(60)

# Run code
if __name__ == "__main__":
    PATH_CONFIG = "./config.txt"
    configurations = neat.config.Config(neat.DefaultGenome,
                                        neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet,
                                        neat.DefaultStagnation,
                                        PATH_CONFIG)
    
    population = neat.Population(configurations)
    population.add_reporter(neat.StdOutReporter(True))
    population_statistics = neat.StatisticsReporter()
    population.add_reporter(population_statistics)

    population.run(racecar_simulator, 1000)