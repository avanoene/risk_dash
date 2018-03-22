from . import market_data as md

class Security(object):

    def __init__(self, name, market_data: md.MarketData, **kwargs):
        self.name = name
        for i in kwargs:
            self.__setattr__(i, kwargs[i])
        self.market_data = market_data

    def valuation(self, current_price):
        pass

class Equity(Security):

    def __init__(self, name, market_data : md.MarketData, ordered_price, quantity):
        self.name = name
        self.market_data = market_data
        self.ordered_price = ordered_price
        self.quantity = quantity

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
        for i in self.port.keys():
            self.port[i].mark_to_market(self.port[i].market_data.currentprice())