### ** _Security**(*name*, *market_data*, **kwargs)

Generic class for Security objects, shouldn't externally be used

#### Parameters
**name** : string identifier for security, i.e. 'AAPL'

**market_data** : MarketData object reference for the Market Data associated with the Security

**kwargs : Generic arguments

#### Attributes
|Attribute| Description|
|---------|------------|


### **Portfolio**(*securities=None*, *input=None*, *apikey=None*)

Main handler for portfolio data. A Portfolio is a collection of Security objects in the `port` dictionary.

#### Parameters
**securities** : array-like of Security objects - should contain all securities in portfolio

**input** : either `pandas.core.frame.DataFrame` or string for csv input path for the method [construct_portfolio_csv(input, apikey)](#construct_portfolio_csv)

**apikey** : String for quandl apikey for the method [construct_portfolio_csv(input, apikey)](#construct_portfolio_csv)

#### Attributes
|Attribute| Description|
|---------|------------|
|[port](#port)| dict of all securities in Portfolio |

#### Methods
|Method | Description |
|-------|-------------|
|[value()](#value)| calculate the current valuation of the portfolio |
|[mark()](#mark)| mark the portfolio at the current market price |
|[get_date()](#get_date)| grab the max date available |
|[set_portfolio_marketdata()](#set_portfolio_marketdata)| combine individual security market_data into one pandas DataFrame |
|[set_port_variance()](#set_port_variance)| set the portfolio variance using weights and covariance matrix |
|[set_weights()](#set_weights)| set the portfolio weights by invested value|
|[construct_portfolio_csv(input, apikey)](#construct_portfolio_csv)| create the portfolio from a .csv matching format portfolio_example.csv|
|[get_portfolio_marketdata()](#get_portfolio_marketdata)| return shared market_data object |
|[get_weights()](#get_weights)| return portfolio weights |
|[get_port_variance()](#get_port_variance)| return value weighted portfolio |

##### **value**()

##### **mark**()

##### **get_date()**

##### **set_portfolio_marketdata()***
