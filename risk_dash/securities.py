from . import market_data as md
import pandas as pd
import numpy as np
from scipy.stats import norm


class _Security(object):

    def __init__(self, name, market_data: md._MarketData, **kwargs):
        self.name = name
        for i in kwargs:
            self.__setattr__(i, kwargs[i])
        self.market_data = market_data

    def valuation(self, current_price):
        pass

    def mark_to_market(self, current_price):
        pass

    def get_marketdata(self):
        return(self.market_data)


class Equity(_Security):

    def __init__(self, ticker, market_data : md.QuandlStockData, ordered_price, quantity, date_ordered):
        self.name = ticker
        self.market_data = market_data
        self.ordered_price = ordered_price
        self.quantity = quantity
        self.initial_value = ordered_price * quantity
        self.date_ordered = date_ordered
        self.type = 'Equity'

    def valuation(self, current_price):
        value = (current_price - self.ordered_price) * self.quantity
        return(value)

    def mark_to_market(self, current_price):
        self.marketvalue = self.quantity * current_price
        change = (current_price - self.ordered_price) * self.quantity
        return(change)


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

    def __init__(self, securities=None, data_input=None, apikey=None):
        if securities:
            port = dict()
            for asset in securities:
                port[asset.name + ' ' + asset.type] = asset
            self.port = port
        elif data_input and apikey:
            self.construct_portfolio_csv(data_input, apikey)
        else:
            self.port = None

    def value(self):
        """
        Value current portfolio with market prices
        :return: value of the portfolio
        """
        value = 0
        for i in self.port.keys():
            value += self.port[i].valuation(self.port[i].market_data.current_price())
        return(value)

    def mark(self):
        """
        Mark portfolio with current market prices, sets marked_portfolio and market_change
        """
        val = 0
        port_val = {}
        for i in self.port.keys():
            temp = self.port[i].mark_to_market(self.port[i].market_data.current_price())
            val += temp
            port_val[i] = (self.port[i].initial_value, self.port[i].marketvalue)
        self.market_change = val
        self.marked_portfolio = port_val

    def get_date(self):
        """
        Grab the latest shared date
        :return: returns a datetime object of the latest shared date
        """
        temp = [len(self.port[i].get_marketdata().market_data.index) for i in self.port.keys()]
        temp = max(temp)
        temp = [self.port[i].get_marketdata().market_data.index
                for i in self.port.keys()
                if len(self.port[i].get_marketdata().market_data.index) == temp]
        return(temp[0])

    def set_portfolio_marketdata(self, key):
        """
        Combine individual market data into one pandas dataframe
        :param key: Common column name for each security
        :return: pandas DataFrame containing columns for each security's common market_data
        """
        try:
            marketdata = pd.DataFrame(index = self.get_date())
            weights = self.get_weights()
            for i in self.port.keys():
                marketdata[i] = self.port[i].get_marketdata().market_data[key]
                marketdata[i + '_port_weighted'] = marketdata[i] * weights[i]
            marketdata = marketdata.interpolate('linear')
            marketdata['portfolio'] = marketdata.loc[:,marketdata.columns.str.contains('_port_weighted')].sum(axis=1)
            self.market_data = marketdata
            return(marketdata)
        except ValueError:
            print('Supply key value in pandas data frame')

    def get_portfolio_marketdata(self, key = None):
        """
        Returns self.market_data
        :param key: If not set, use key to set market_data
        :return: pandas DataFrame self.market_data
        """
        try:
            return self.market_data
        except:
            self.set_portfolio_marketdata(key)
            return self.market_data

    def set_weights(self):
        """
        Calculate value weighted portfolio
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

    def set_port_variance(self, confidence_interval = norm.pdf(.025)):
        """
        Calulates parametric Variance by calculating Weight**-1 * Cov * Weight
        :param confidence_interval: For value at risk, what distribution score - default 1.96 for normal distribution
        :return: float portfolio variance
        """
        weights = self.get_weights()
        covar = self.market_data.loc[:, ~self.market_data.columns.str.contains('port')].cov()
        order = covar.columns
        weight_array = np.array([weights[i] for i in order])
        cov_mat = np.array(covar)
        variance = np.matmul(np.matmul(weight_array.T, cov_mat), weight_array)
        self.port_variance = variance
        self.parametric_portfolio_value_at_risk = variance * confidence_interval
        return(variance)

    def get_port_variance(self):
        """
        Returns portfolio variance
        :return:
        """
        try:
            return(self.port_variance, self.parametric_portfolio_value_at_risk)
        except:
            self.set_port_variance()
            return (self.port_variance, self.parametric_portfolio_value_at_risk)

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
        return(self.port)
