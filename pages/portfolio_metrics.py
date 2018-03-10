from objects import market_data as md, securities as sec
import pandas as pd
from apiconfig import quandl_apikey as apikey

userinput = pd.read_excel('input_test.xlsx')

def create_portoflio(input):
    temp = []
    for i in input.index:
        tempdata = md.QuandlStockData(apikey, input.loc[i, 'Ticker'], days=80)
        tempsecurity = sec.Equity(input.loc[i, 'Ticker'],
                                  tempdata,
                                  ordered_price=input.loc[i, 'Ordered Price'],
                                  quantity=input.loc[i, 'Quantity'])
        temp.append(tempsecurity)
    outport = sec.Portfolio(temp)
    return(outport)

