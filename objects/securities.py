from . import market_data as md
import pandas as pd
import numpy as np

class Security(object):

    def __init__(self, name, market_data: md.MarketData, **kwargs):
        self.name = name
        for i in kwargs:
            self.__setattr__(i, kwargs[i])
        self.market_data = market_data

    def valuation(self, current_price):
        pass

    def get_marketdata(self):
        return(self.market_data)

class Equity(Security):

    def __init__(self, name, market_data : md.MarketData, ordered_price, quantity):
        self.name = name
        self.market_data = market_data
        self.ordered_price = ordered_price
        self.quantity = quantity
        self.initial_value = ordered_price * quantity

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

    def __init__(self, securities : Security):
        port = dict()
        for i in securities:
            port[i.name] = i
        self.port = port

    def value(self):
        value = 0
        for i in self.port.keys():
            value += self.port[i].valuation(self.port[i].market_data.currentprice())
        return(value)

    def mark(self):
        val = 0
        port_val = {}
        for i in self.port.keys():
            temp = self.port[i].mark_to_market(self.port[i].market_data.currentprice())
            val += temp
            port_val[i] = (self.port[i].initial_value, self.port[i].marketvalue)
        self.market_change = val
        self.marked_portfolio = port_val

    def get_date(self):
        temp = [len(self.port[i].get_marketdata().market_data.index) for i in self.port.keys()]
        temp = max(temp)
        temp = [self.port[i].get_marketdata().market_data.index
                for i in self.port.keys()
                if len(self.port[i].get_marketdata().market_data.index) == temp]
        return(temp[0])

    def set_portfolio_marketdata(self, key):
        marketdata = pd.DataFrame(index = self.get_date())
        weights = self.get_weights()
        for i in self.port.keys():
            marketdata[i] = self.port[i].get_marketdata().market_data[key]
            marketdata[i + '_port_weighted'] = marketdata[i] * weights[i]
        marketdata = marketdata.interpolate('linear')
        marketdata['portfolio'] = marketdata.loc[:,marketdata.columns.str.contains('_port_weighted')].sum(axis=1)
        self.market_data = marketdata
        return(marketdata)

    def get_weights(self):
        port_val = {
            i : j.quantity * j.ordered_price
            for i, j in self.port.items()
        }
        total_val = sum(port_val.values())
        weights = {
            i: j / total_val
            for i, j in port_val.items()
        }
        self.weights = weights
        return(weights)

    def get_port_variance(self):
        weights = self.get_weights()
        covar = self.market_data.loc[:, ~self.market_data.columns.str.contains('port')].cov()
        order = covar.columns
        weight_array = np.array([weights[i] for i in order])
        cov_mat = np.array(covar)
        variance = np.matmul(np.matmul(weight_array.T, cov_mat), weight_array)
        self.port_variance = variance
        return(variance)
