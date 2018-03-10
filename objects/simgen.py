import pandas as pd
import numpy as np
from objects import market_data

class RandomGen():
    def __init__(self, location, scale):
        self.location = location
        self.scale = scale

    def generate(self, **kwargs):
        pass

class Simulation():
    def __init__(self, gen: RandomGen, **kwargs):
        self.Generator = gen
        self.simulated_distribution = self.Generator.generate(**kwargs)

class NormalDistribution(RandomGen):

    def generate(self, obs):
        return(np.random.normal(self.location, self.scale, obs))

class NaiveMonteCarlo(Simulation):

    def set_var(self):
        self.percentilevar = np.percentile(self.simulated_distribution, 2.5)





