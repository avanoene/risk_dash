from . import market_data as mc

class Security(object):

    def __init__(self, name, market_data: mc.MarketData, **kwargs):
        self.name = name
        for i, j in kwargs:
            self.i = self.j
        self.market_data = market_data

    def valuation(self, current_price):
        pass

class Equity(Security):

    def valuation(self, current_price):
        value = self.ordered_price * self.quantity - current_price
        return(value)


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

    port = dict()

    def __init__(self, securities):
        for i in securities:
            self.port[securities.name] = securities
