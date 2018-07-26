import pandas as pd
import numpy as np
from . import market_data

class _RandomGen():
    def __init__(self, **kwargs):
        self.args = {
            name: argument
            for name, argument in kwargs.items()
        }

    def generate(self, **kwargs):
        pass

class _Simulation():

    def __init__(self, Generator: _RandomGen, **kwargs):
        self.Generator = Generator
        self.args = {
            name : argument
            for name, argument in kwargs.items()
        }

    def simulate(self, number_of_simulations):
        pass


class NormalDistribution(_RandomGen):

    def __init__(self, location, scale):
        self.args = {
            'location': location,
            'scale': scale
        }

    def generate(self, obs):
        return(np.random.normal(self.args['location'], self.args['scale'], obs))


class NaiveMonteCarlo(_Simulation):

    def simulate(self, periods_forward, number_of_simulations):
        """

        :param periods_forward:
        :param number_of_simulations:
        :return:
        """
        simulations = [self.Geneprator.generate(periods_forward) for i in range(number_of_simulations)]

        simulations = [simulation.cumsum() for simulation in simulations]

        simulations = np.array(simulations)

        self.simulation_mean = simulations.mean(axis=0)

        self.simulation_std = simulations.std(axis=0)

        self.simulated_distribution = simulations[:,-1]

        return(simulations)

    def set_var(self):
        self.percentilevar = np.percentile(self.simulated_distribution, 2.5)





