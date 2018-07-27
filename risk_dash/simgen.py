import pandas as pd
import numpy as np
from . import market_data
from statsmodels.tsa.arima_model import ARMA

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
        simulations = [self.Generator.generate(periods_forward) for i in range(number_of_simulations)]

        simulations = [simulation.cumsum() for simulation in simulations]

        simulations = np.array(simulations)

        self.simulation_mean = simulations.mean(axis=0)

        self.simulation_std = simulations.std(axis=0)

        self.simulated_distribution = simulations[:, -1]

        return(simulations)

    def set_var(self):
        self.percentilevar = np.percentile(self.simulated_distribution, 2.5, axis=0)

class HistoricPull(_RandomGen):

    def generate(self, num_obs, day_list):
        return np.random.choice(day_list, num_obs)

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

