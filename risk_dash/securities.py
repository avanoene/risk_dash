from . import market_data as md
import pandas as pd
import numpy as np
from scipy.stats import norm, t


class _Security(object):
    """
    Template for _Security subclasses
    """

    def __init__(self, name, market_data: md._MarketData, **kwargs):
        self.name = name
        for i in kwargs:
            self.__setattr__(i, kwargs[i])
        self.market_data = market_data

    def valuation(self, price):
        pass

    def mark_to_market(self, current_price):
        pass

    def get_marketdata(self):
        return(self.market_data)

    def simulate(self, SimulationGenerator, periods_forward, number_of_simulations):
        pass


class Equity(_Security):

    def __init__(self, ticker, market_data : md.QuandlStockData, ordered_price, quantity, date_ordered):
        """

        :param ticker:
        :param market_data:
        :param ordered_price:
        :param quantity:
        :param date_ordered:
        """
        self.name = ticker
        self.market_data = market_data
        self.ordered_price = ordered_price
        self.quantity = quantity
        self.initial_value = ordered_price * quantity
        self.date_ordered = date_ordered
        self.type = 'Equity'

    def valuation(self, price):
        value = (price - self.ordered_price) * self.quantity
        return(value)

    def mark_to_market(self, current_price):
        self.market_value = self.quantity * current_price
        self.marked_change = self.valuation(current_price)
        return(self.marked_change)
    def simulate(self, SimulationGenerator, periods_forward, number_of_simulations):
        self.all_sims = SimulationGenerator.simulate(periods_forward, number_of_simulations)
        self.simulation_mean = SimulationGenerator.simulation_mean
        self.simulation_std = SimulationGenerator.simulation_std
        self.simulated_distribution = SimulationGenerator.simulated_distribution

        return self.simulation_mean, self.simulation_std

class Trade(object):

    def __init__(self, securities):
        self.securities = securities
        self.trade_value = [0]

    def value(self, current_prices):
        value = 0
        for i in self.securities:
            value += i.valuation(current_prices[i.name])

    def step(self, date, **kwargs):
        self.choice()
        current_prices = []
        for i in self.securities:
            current_prices[i.name] = i.market_data.loc[i.market_data['datelab'] == kwargs['date'], kwargs['pricelab']]
        self.trade_value.append(self.value(current_prices))

    def choice(self):
        pass

class Portfolio(object):
    """
    The Portfolio class handles interactions with the portfolio data and the associated securities in the portfolio.

    :param securities:
    :param data_input:
    :param apikey:

    """

    def __init__(self, securities=None, data_input=None, apikey=None):
        if securities:
            for asset in securities:
                self.add_security(asset)
        elif data_input and apikey:
            self.construct_portfolio_csv(data_input, apikey)
        else:
            self.port = None

    def add_security(self, security, overwrite=True):
        if self.port is not None:
            if (security.name + ' ' + security.type not in self.port.keys()) or overwrite:
                self.port[security.name + ' ' + security.type] = security
            else:
                raise Exception('Security type and name already in portfolio')
        else:
            self.port = dict()
            self.port[security.name + ' ' + security.type] = security

    def remove_security(self, security=None, security_name=None, security_type=None):
        try:
            if security:
                self.port.pop(security.name + ' ' + security.type)
            elif security_name and security_type:
                self.port.pop(security_name + ' ' + security_type)
            else:
                raise Exception('Must pass in either security or name and type')
        except KeyError:
            raise Exception('Security not in portfolio')

    def value(self):
        """
        Value current portfolio with current market prices.

        :return: value of the portfolio

        """
        value = 0
        for i in self.port.keys():
            value += self.port[i].valuation(self.port[i].market_data.current_price())
        return value

    def mark(self):
        """
        Mark portfolio with current market prices, sets marked_portfolio and market_change.
        """
        val = 0
        port_val = {}
        for i in self.port.keys():
            temp = self.port[i].mark_to_market(self.port[i].market_data.current_price())
            val += temp
            port_val[i] = (self.port[i].initial_value, self.port[i].market_value)
        self.market_change = val
        self.marked_portfolio = port_val
        self.date_marked = self.get_last_shared_date()
        self.initial_value = sum(port_val[i][0] for i in port_val.keys())

    def get_date(self):
        """
        Grab the security with the most dates.

        :return: returns a DatetimeIndex to construct a shared portfolio market_data DataFrame

        """
        temp = [len(self.port[i].get_marketdata().market_data.index) for i in self.port.keys()]
        temp = max(temp)
        temp = [self.port[i].get_marketdata().market_data.index
                for i in self.port.keys()
                if len(self.port[i].get_marketdata().market_data.index) == temp]
        return temp[0]

    def get_last_shared_date(self):
        """
        Return the last shared date

        :return: DateTime object

        """
        temp = min(
            self.port[i].get_marketdata().market_data.index[-1]
            for i in self.port.keys()
        )
        return temp

    def set_portfolio_marketdata(self, key):
        """
        Combine individual market data into one pandas DataFrame.

        :param key: Common column name for each security

        :return: pandas DataFrame containing columns for each security's common market_data

        """
        try:
            marketdata = pd.DataFrame(index = self.get_date())
            weights = self.get_weights()
            for i in self.port.keys():
                marketdata[i] = self.port[i].get_marketdata().market_data[key]
                marketdata[i + '_port_weighted'] = marketdata[i] * weights[i]
            marketdata = marketdata.dropna()
            marketdata = marketdata.interpolate('linear').bfill()
            marketdata['portfolio'] = marketdata.loc[:,marketdata.columns.str.contains('_port_weighted')].sum(axis=1)
            self.market_data = marketdata
            self.market_data_key = key
            return(marketdata)
        except ValueError:
            print('Supply key value in pandas data frame')

    def get_portfolio_marketdata(self, key = None, recalc=False):
        """
        Returns self.market_data

        :param key: If not set, use key to set market_data

        :return: pandas DataFrame self.market_data

        """
        if key or recalc or (key != self.market_data_key):
            self.set_portfolio_marketdata(key)
            return self.market_data
        else:
            try:
                return self.market_data
            except:
                raise Exception("Must set market_data with .set_portfolio_marketdata()")

    def calculate_portfolio_returns(self, market_data):
        """
        Calculates market data returns from flat prices

        :param market_data: the market_data variable with a flat price values

        :return: the market_data variable with log returns

        """
        short_positions = (
            np.log(-1 * market_data.loc[:, market_data.apply(np.max) < 0])
            - np.log(-1 * market_data.loc[:, market_data.apply(np.max) < 0].shift(1))
        )
        long_positions = (
            np.log(market_data.loc[:, market_data.apply(np.max) > 0])
            - np.log(market_data.loc[:, market_data.apply(np.max) > 0].shift(1))
        )
        market_data = long_positions.join(short_positions)
        return market_data

    def quick_plot(self, returns = True, key = 'adj_close', plot=True, figsize = (5,8)):
        """
        Quickly plot using matplotlib and pandas.plot()

        :param returns: Bool, True if calculate DD based on continuous returns, False if on level prices
        :param key: string, corresponds to the market_data column to be calculated
        :param plot: Bool, if True, plot the data frame, if flase just return the market_data DataFrame

        :return: DataFrame market_data

        """

        market_data = self.get_portfolio_marketdata(key)
        market_data = market_data.loc[
            :,
            market_data.columns.str.contains('port')
        ]
        if returns == True:
            market_data = self.calculate_portfolio_returns(market_data)
        if plot and returns:
            np.exp(market_data.cumsum()).plot(figsize=figsize)
        elif plot and not returns:
            market_data.plot(figsize=figsize)
        else:
            return market_data
        return market_data


    def set_weights(self):
        """
        Calculate value weighted portfolio.

        :return: dict for each security weight

        """
        port_val = {
            name : security.quantity * security.ordered_price
            for name, security in self.port.items()
        }
        total_val = sum(port_val.values())
        weights = {
            name : security_value / total_val
            for name, security_value in port_val.items()
        }
        self.weights = weights
        return(weights)

    def get_weights(self):
        """
        Returns self.weights

        :return: dict for each security weight

        """
        try:
            return self.weights
        except:
            self.set_weights()
            return self.weights

    def set_port_variance(self, market_data=None, confidence_interval = norm.ppf(.025), var_horizon = 10, lookback_periods=0, key='percentchange'):
        """
        Calulates parametric Variance by calculating Weight.T * Cov * Weight

        :param market_data: DataFrame, the portfolio level market_data. Use if made external changes to the market_data
        :param confidence_interval: float, The critical value to implement parametric VaR
        :param var_horizon: int, how many days/periods forward the parametric VaR should be calculated
        :param lookback_periods: int, how many days/periods backward to condition the underlying distribution
        :param key: string, corresponds to the market_data column to be calculated

        :return: float portfolio variance, standard deviation ** 2, float parametric value at risk

        """
        if market_data is None:
            market_data = self.get_portfolio_marketdata(key)
        if lookback_periods == 0:
            covar = market_data.loc[:, ~market_data.columns.str.contains('port')].cov()
        else:
            covar = market_data.loc[
                market_data.index[-lookback_periods:],
                ~market_data.columns.str.contains('port')
            ].cov()
        weights = self.get_weights()
        order = covar.columns
        weight_array = np.array([weights[i] for i in order])
        cov_mat = np.array(covar)
        variance = np.matmul(np.matmul(weight_array.T, cov_mat), weight_array)
        if lookback_periods == 0:
            VaR = np.sqrt(variance * var_horizon) * confidence_interval
        else:
            VaR = np.sqrt(variance * var_horizon) * t.ppf(.025, df=lookback_periods-1)
        self.cov = covar
        self.port_variance = variance
        self.parametric_portfolio_value_at_risk = VaR
        return variance, VaR

    def get_port_variance(self, recalc=False, confidence_interval = norm.pdf(.025), var_horizon = 10, lookback_periods=0, key=None):
        """
        Returns portfolio variance

        :param recalc: bool, If True recalculate variance
        :param confidence_interval: float, The critical value to implement parametric VaR
        :param var_horizon: int, how many days/periods forward the parametric VaR should be calculated
        :param lookback_periods: int, how many days/periods backward to condition the underlying distribution
        :param key: string, corresponds to the market_data column to be calculated

        :return: tuple: (float Var(Portfolio), float Parametric Portfolio V@R)

        """
        if key or recalc:
            self.set_port_variance(key=key, confidence_interval=confidence_interval, var_horizon=var_horizon,lookback_periods=lookback_periods)
        try:
            return self.port_variance, self.parametric_portfolio_value_at_risk
        except:
            raise Exception('Must set port_variance with .set_port_variance()')

    def historic_var(self, market_data=None, returns=True, key='adj_close', confidence=2.5, var_horizon=10):
        """
        Calulate Value at Risk from the historic distrubtion

        :param market_data: DataFrame, the portfolio level market_data. Use if made external changes to the market_data
        :param returns: Bool, True if calculate DD based on continuous returns, False if on level prices
        :param key: string, corresponds to the market_data column to be calculated
        :param confidence: float, percentile in percentage to pass into np.percentile
        :param var_horizon: int, how many days/periods forward the parametric VaR should be calculated

        :return: tuple, (DataFrame, market_data, float, Historic VaR)

        """
        if market_data is None:
            market_data = self.get_portfolio_marketdata(key)

        if returns:
            market_data = self.calculate_portfolio_returns(market_data)
            market_data = market_data.rolling(var_horizon).sum()
            market_data = np.exp(market_data) - 1
        else:
            market_data = market_data.diff(1)
            market_data = market_data.rolling(var_horizon).sum()

        self.historic_portfolio_value_at_risk = np.nanpercentile(market_data['portfolio'], confidence)
        return market_data, np.nanpercentile(market_data['portfolio'], confidence)

    def drawdown(self, market_data=None, returns=True, key='adj_close'):
        """
        Calculate Draw Down, the previous peak to current trough, through the historic market data

        :param market_data: DataFrame, the portfolio level market_data. Use if made external changes to the market_data
        :param returns: Bool, True if calculate DD based on continuous returns, False if on level prices
        :param key: string, corresponds to the market_data column to be calculated

        :return: DataFrame representing the Draw Down for the portfolio and components

        """
        if market_data is None:
            market_data = self.get_portfolio_marketdata(key)
        if returns:
            market_data = self.calculate_portfolio_returns(market_data)
            market_data = market_data.cumsum() - market_data.cumsum().cummax()
            market_data = np.exp(market_data)
        else:
            market_data = market_data.cummax() - market_data
        return market_data



    def construct_portfolio_csv(self, data_input, apikey):
        """
        Built in portfolio constructor method

        :param data_input: either pandas DataFrame or string path to a portfolio matching './portfolio_example.csv'
        :param apikey: ApiKey for the market data object

        :return: dict for self.port

        """
        assets = []

        if type(data_input) == str:
            portfolio_data = pd.read_csv(data_input)
        elif type(data_input) == pd.core.frame.DataFrame:
            portfolio_data = data_input
        else:
            print('Not parseable')
            self.port = None
            return(self.port)

        for i in portfolio_data.index:
            if portfolio_data.loc[i, 'Type'] == 'Equity':
                tempdata = md.QuandlStockData(apikey, portfolio_data.loc[i, 'Ticker'], days=80)
                tempsecurity = Equity(
                    portfolio_data.loc[i, 'Ticker'],
                    tempdata,
                    ordered_price = portfolio_data.loc[i, 'Ordered Price'],
                    quantity = portfolio_data.loc[i, 'Quantity'],
                    date_ordered=portfolio_data.loc[i, 'Ordered Date']
                )
                assets.append(tempsecurity)
            else:
                print('Type of security not defined!')
                self.port = None
                return(self.port)
        self.port = {asset.name + ' ' + asset.type : asset for asset in assets}
        return self.port

    def simulate(self, SimulationGenerator, periods_forward, number_of_simulations):
        self.all_sims = SimulationGenerator.simulate(periods_forward, number_of_simulations)
        self.simulation_mean = SimulationGenerator.simulation_mean
        self.simulation_std = SimulationGenerator.simulation_std
        self.simulated_distribution = SimulationGenerator.simulated_distribution

        return self.simulation_mean, self.simulation_std

