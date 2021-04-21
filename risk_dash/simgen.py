import pandas as pd
import numpy as np
from . import market_data
from statsmodels.tsa.arima_model import ARMA

class _RandomGen():

    """
    Abstract class for a Random Variable Generator

    :param kwargs: dict, a collection of necessary arguments to specify the RV distribution. See .NormalDistribution for an example
    """

    def __init__(self, **kwargs):
        self.args = {
            name: argument
            for name, argument in kwargs.items()
        }

    def generate(self, **kwargs):
        """
        Function to generate random values given the RV distribution or other method of generating values
        """
        raise NotImplementedError()

class _Simulation():

    """
    Abstract class to create a simulation given a Random Variable Generator

    :param Generator: _RandomGen, the RV distribution to use for a given simulation. See .NaiveMonteCarlo for an example
    """

    def __init__(self, Generator: _RandomGen, **kwargs):
        self.Generator = Generator
        self.args = {
            name : argument
            for name, argument in kwargs.items()
        }

    def set_var(self, percentile=2.5):
        """
        Helper function to set Value at Risk given a certain percentile

        :param percentile: float, default 2.5, represents the Value at Risk, as defined by a certain percentile, for a simulation

        """
        self.percentilevar = np.percentile(self.simulated_distribution, percentile, axis=0)

    def simulate(self, number_of_simulations):
        pass


class NormalDistribution(_RandomGen):
    """
    A _RandomGen object that represents a normal/Gaussian. See [numpy documentation](https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html) for more detail

    :param location: float, the mean/center of the distribution
    :param scale: float, the standard deviation of the distribution. Must be non-negative.
    """

    def __init__(self, location, scale):
        self.args = {
            'location': location,
            'scale': scale
        }

    def generate(self, obs):
        """
        Function to return a numpy.array of parametrically defined normally distributed random values

        :param obs: int, number of values to be generated

        :return: numpy.array of numpy.float, represents a collection of randomly distributed values
        """
        return(np.random.normal(self.args['location'], self.args['scale'], obs))


class NaiveMonteCarlo(_Simulation):

    """
    A _Simulation object to create a Naive Monte Carlo simulation of a Random Walk, with each step being i.i.d. given the _RandomGen RV Generator class
    """

    def simulate(self, periods_forward, number_of_simulations):
        """
        Function to simulate each independent walk in the Monte Carlo simulation

        :param periods_forward: int, how many steps into the future each random simulated random walk will take
        :param number_of_simulations: int, how many separate independent paths will be simulated

        :return: np.array of shape (periods_forward, number_of_simulations), each row is an independent simulation, each column is a time period step
        """
        simulations = [self.Generator.generate(periods_forward) for i in range(number_of_simulations)]

        simulations = [simulation.cumsum() for simulation in simulations]

        simulations = np.array(simulations)

        self.simulation_mean = simulations.mean(axis=0)

        self.simulation_std = simulations.std(axis=0)

        self.simulated_distribution = simulations[:, -1]

        return(simulations)



class HistoricPull(_RandomGen):

    """
    A _RandomGen object that represents a uniformly distributed selection from a given set of historic observations
    """

    def generate(self, obs, historic_observations):
        """
        Function to return a numpy.array of randomly and uniformly selected values from the given historic observations

        :param obs: int, number of observations to pull
        :param historic_observations: list-like float, the collection of historic observations to pull from

        :return: np.array of selected historic observations
        """
        return np.random.choice(historic_observations, obs)

class HistoricFilteredSimulation(_Simulation):

    def fit(self, market_data):
        arma_model = ARMA(market_data, (1, 1))
        arma_res = arma_model.fit(method='mle', disp=0, start_ar_lags=10)
        garch_model = ARMA(np.square(arma_res.resid), (1, 1))
        garch_res = garch_model.fit(method='mle', disp=0, start_ar_lags=10)
        garch_parameters = garch_res.params
        standardized = np.square(np.array([arma_res.resid]))

        return garch_parameters, garch_res, arma_res.resid, market_data

    def simulate(self, periods_forward, number_of_simulations, market_data):
        garch_values, model, residuals = self.fit(market_data)


class BinomialDistribtion(_RandomGen):

    def __init__(self, location, scale, probability=None):
        self.scale = scale
        self.location = location
        if probability:
            self.probability = probability
        else:
            up = np.exp(scale)
            down = 1/up
            self.probability = (np.exp(location) - down) / (up - down)

    def generate(self, n, obs):
        return np.random.binomial(n, self.probability, obs)

class CRRBinomialTree(_Simulation):

    def simulate(self, vol, periods_forward, number_of_simulations, resolution=None):

        # Allow to adjust for partial days and more granularity
        if resolution:
            up = np.exp(self.Generator.location/resolution + vol*np.sqrt(1/resolution))
            down = np.exp(self.Generator.location/resolution - vol*np.sqrt(1/resolution))
            self.Generator.probability = (np.exp(self.Generator.location/resolution) - down) / (up - down)
        else:
            up = np.exp(self.Generator.location + vol)
            down = np.exp(self.Generator.location - vol)

        # Simulate a Bernoulli RV for every time step
        simulations = np.array([
            self.Generator.generate(1, number_of_simulations)
            for n in range(periods_forward)
            ])
        # Cumulative Bernoulli RV for each path
        simulations = simulations.cumsum(axis = 0)
        simulations = np.array([
            np.power(up, simulations[n]) * np.power(down, ((n+1) - simulations[n]))
            for n in range(periods_forward)
        ])
        simulations = np.log(simulations.T)
        self.simulation_mean = simulations.mean(axis=0)
        self.simulation_std = simulations.std(axis=0)
        self.simulated_distribution = simulations[:, -1]

        return simulations

