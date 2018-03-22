import quandl
import requests
import pandas as pd
from dateutil.relativedelta import relativedelta
import numpy as np


class MarketData(object):

    def __init__(self):
        self.market_data = self.gather()

    def gather(self):
        pass
    def currentprice(self):
        pass

class QuandlStockData(MarketData):

    def __init__(self, apikey, ticker, days=80):
        self.apikey = apikey
        self.ticker = ticker
        self.market_data = self.gather()
        self.maxdate = max(self.market_data['date'])
        self.set_volatility(days)
        self.set_expected(days)


    def gather(self):
        quandl.ApiConfig.api_key = self.apikey
        # this would be where I would construct it's own api call, using quandl's get_table method instead
        #base = quandl.ApiConfig.api_base
        #base += '/datatables/' + querypattern + '&api_key=' + apikey
        #data = requests.get(base)
        metadata = quandl.Dataset('WIKI/' + self.ticker)
        date = metadata['newest_available_date']
        data = quandl.get_table('WIKI/PRICES',
                                ticker=self.ticker,
                                date={'gte':(date - relativedelta(years=5))})
        return(data)

    def setpricechanges(self):
        self.market_data['pricechange'] = self.market_data['adj_close'].diff(1)
        self.market_data['percentchange'] = np.log(self.market_data['adj_close']) - np.log(self.market_data['adj_close'].shift(1))
    def set_volatility(self, days):
        self.setpricechanges()
        self.market_data['exp_volatility'] = self.market_data['percentchange'].ewm(span=days,min_periods=days).std()
        self.market_data['sw_volatility'] = self.market_data['percentchange'].rolling(days).std()
        self.currentexvol = self.market_data.loc[self.market_data['date']==self.maxdate, 'exp_volatility'].values[0]
        self.currentswvol = self.market_data.loc[self.market_data['date']==self.maxdate, 'sw_volatility'].values[0]
    def set_expected(self, days):
        self.market_data['exp_average_dailyincrease'] = self.market_data['percentchange'].ewm(span=days, min_periods=days).mean()
        self.market_data['sw_average_dailyincrease'] = self.market_data['percentchange'].rolling(days).mean()
        self.currentexmean = self.market_data.loc[self.market_data['date']==self.maxdate, 'exp_average_dailyincrease'].values[0]
        self.currentswmean = self.market_data.loc[self.market_data['date']==self.maxdate, 'sw_average_dailyincrease'].values[0]

    def currentprice(self):
        return(self.market_data.loc[self.market_data['date']==self.maxdate, 'adj_close'].values[0])




