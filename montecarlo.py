import pandas as pd
import numpy as np

class MarketData:
    def __init__(self, market_data, days):
        self.market_data = market_data
        self.days = days
        self.maxdate = max(self.market_data['adj_close'])
        self.set_volatility(days)
        self.set_expected(days)

    def setpricechanges(self):
        self.market_data['pricechange'] = self.market_data['adj_close'].diff(1)
        self.market_data['percentchange'] = np.log(self.market_data['adj_close']) - np.log(self.market_data['adj_close'].shift(1))
    def set_volatility(self, days):
        self.setpricechanges()
        self.market_data['exp_volatility'] = self.market_data['percentchange'].ewm(span=days,min_periods=days).std()
        self.market_data['sw_volatility'] = self.market_data['percentchange'].rolling(days).std()
        self.currentexvol = self.market_data.loc[self.market_data['adj_close']==self.maxdate, 'exp_volatility']
        self.currentswvol = self.market_data.loc[self.market_data['adj_close']==self.maxdate, 'sw_volatility']
    def set_expected(self,days):
        self.market_data['exp_average_dailyincrease'] = self.market_data['percentchange'].ewm(span=days, min_periods=days).mean()
        self.market_data['sw_average_dailyincrease'] = self.market_data['percentchange'].rolling(days).mean()
        self.currentexmean = self.market_data.loc[self.market_data['adj_close']==self.maxdate, 'exp_average_dailyincrease']
        self.currentswmean = self.market_data.loc[self.market_data['adj_close']==self.maxdate, 'sw_average_dailyincrease']


class RandomGen():
    def __init__(self, location, scale):
        self.location = location
        self.scale = scale
    def normaldist(self, numobs):
        self.obs = np.random.normal(self.location, self.scale, numobs)

class MonteCarlo(MarketData):
    def __init__(self,market_data, days, exp = True):
        MarketData.__init__(self,market_data,days)
        if exp == True:
            self.gen = RandomGen(location=self.currentexmean, scale=self.currentexvol)
        else:
            self.gen = RandomGen(location=self.currentswvol,
                                 scale=self.currentswvol)




