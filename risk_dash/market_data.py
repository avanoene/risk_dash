import quandl
import requests
import pandas as pd
from dateutil.relativedelta import relativedelta
import numpy as np


class _MarketData(object):
    """
    Template for _MarketData subclasses
    """
    
    def __init__(self):

        self.market_data = self.gather()

    def gather(self):
        """
        This should gather data from the source and store it into memory or dictate how to interact with the source

        :return: a pandas DataFrame, market_data or other data type to interact with

        """
        raise NotImplementedError

    def current_price(self):
        """
        This should return the current market price, the price at the last available time period

        :return: float the market price

        """
        raise NotImplementedError

    def set_price_changes(self):
        raise NotImplementedError

    def set_volatility(self, days):
        raise NotImplementedError

    def set_expected(self, days):
        raise NotImplementedError


class QuandlStockData(_MarketData):
    """
    _MarketData class for Quandl's WIKI/EOD price data base (https://www.quandl.com/databases/WIKIP)

    :param apikey: string, a valid Quandl apikey
    :param ticker: string, ticker symbol to query
    :param days: int, how many days back to use for rolling metrics
    """

    def __init__(self, apikey, ticker, days=80):

        self.apikey = apikey
        self.ticker = ticker
        self.market_data = self.gather()
        self.market_data.index = self.market_data['date']
        self.market_data = self.market_data.sort_index()
        self.maxdate = max(self.market_data['date'])
        self.set_volatility(days)
        self.set_expected(days)


    def gather(self):
        """
        Gathers the data from the Quandl api and returns a pandas DataFrame

        :return: pandas DataFrame

        """
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

    def set_price_changes(self):
        """
        Set daily price changes and logged percent changes
        """
        self.market_data['pricechange'] = self.market_data['adj_close'].diff(1)
        self.market_data['percentchange'] = (np.log(self.market_data['adj_close']) - np.log(self.market_data['adj_close'].shift(1))).fillna(0)


    def set_volatility(self, days):
        """
        Calculate exponentially and simply weighted rolling standard deviations

        :param days: int, look back days to compute rolling std deviation

        """
        self.set_price_changes()
        self.market_data['exp_volatility'] = self.market_data['percentchange'].ewm(span=days,min_periods=days).std()
        self.market_data['sw_volatility'] = self.market_data['percentchange'].rolling(days).std()
        self.currentexvol = self.market_data.loc[self.market_data['date']==self.maxdate, 'exp_volatility'].values[0]
        self.currentswvol = self.market_data.loc[self.market_data['date']==self.maxdate, 'sw_volatility'].values[0]

    def set_expected(self, days):
        """
        Calculate exponentially and simply weighted rolling averages

        :param days: int, look back days to compute rolling averages

        """
        self.market_data['exp_average_dailyincrease'] = self.market_data['percentchange'].ewm(span=days, min_periods=days).mean()
        self.market_data['sw_average_dailyincrease'] = self.market_data['percentchange'].rolling(days).mean()
        self.currentexmean = self.market_data.loc[self.market_data['date']==self.maxdate, 'exp_average_dailyincrease'].values[0]
        self.currentswmean = self.market_data.loc[self.market_data['date']==self.maxdate, 'sw_average_dailyincrease'].values[0]

    def current_price(self):
        """
        Returns the latest available market price

        :return: float, latest available market price

        """
        return(self.market_data.loc[self.market_data['date']==self.maxdate, 'adj_close'].values[0])




