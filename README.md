# risk_dash

[risk_dash](https://github.com/avanoene/risk_dash) is a framework to help simplify the data flow for a portfolio of assets and handle market risk metrics at the asset and portfolio level. If you clone the source [repository](https://github.com/avanoene/risk_dash), included is a [Dash](https://plot.ly/dash/) application to be an example of some of the uses for the package.

## Disclaimer: Due to data issues, only up to March 28th EOD is available from Quandl's WIKI EOD Stock Prices found in the example application.

Thesis Proposal: First create a framework package, risk_dash, to handle a portfolio of assets, then create a risk application to calculate and display common risk factors and metrics to present common uses for the framework, including: Value at Risk, Expected Portfolio Return and Volatility, Current Return, Systematic risk (Fama - French / CAPM)

To accomplish this task, I am planning on using current research and python packages. I am planning on using [Dash by Plotly](https://plot.ly/dash/) to create the front end user interface and deploying the underlying Flask app on either [DigitalOcean](https://www.digitalocean.com/) or [Heroku](https://www.heroku.com/)

The object model is housed in `~/risk_dash/` where as the application pages are in `~/pages/` and are managed by `/dashapp.py`

While risk_dash only needs a few dependencies,[pandas](https://pandas.pydata.org/), [numpy](http://www.numpy.org/), [scipy](https://www.scipy.org/), and [requests](http://docs.python-requests.org/en/master/), the included application uses the dependencies listed in [requirements.txt](https://github.com/avanoene/risk_dash/requirements.txt) which can be installed by:

```pip install -r requirements.txt```

It is highly recommended that you should use a virtual environment when running the package, for details check the [Python documentation](https://docs.python.org/3/tutorial/venv.html)

## Getting Started - Locally Running the Dash App

First add file `apiconfig.py` to the directory at the same level as `dashapp.py`. That file should contain all of the api information to source the market data. I'm using [Quandl](https://www.quandl.com/) so my `apiconfig.py` file is the following:

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

quandl_apikey = 'quandl-api-key' # replace with valid key
```

To use a different market data source, first write a specific `MarketData` class in `market_data.py`

To run the server locally using the underlying Flask Server, run the following command:

```
python dashapp.py
```

If you wanted to use `gunicorn` to run the server, you would just run `gunicorn dashapp:server` from the command line.

## Documentation

Hosted documentation is coming soon. Below is a high level overview of the project:

### Object Model

The framework seeks to address a solution to the data pipeline, since the scale is managiable within memory at the moment, that pipeline includes:

- Gathering required data from source systems, i.e. market data, portfolio data, security data
- Managing that data, potentially storing as scale increases
- Manipulating to create new data
- Returning or storing results

To handle that pipeline, the current model is:

- Portfolio
  - Security
- SimulationGenerator
- MarketData
- FundamentalData (Not implemented)

MarketData objects should be the source of the data for a particular Security (or underlier if a derivative security), attributes:
- Prices
- Source engine (where the data comes from)
- Common metrics (first integrated series 'daily price change', shape, dispersion)

SimulationGenerator objects should dictate how any simulation should be conducted, attributes:
- Transformation methods
- Number of observations
- Lookback period, if necessary

Security objects could be any asset, those assets have:
- Market Data
- Value Function
- Approprate SimulationGenerator as default, pass in a SimulationGenerator
- Risk Attributes
- Fundamental Data

The Portfolio object as a collection of Security objects and potentially other Portfolio objects, since we could have different hierarchal structures within the book
- This then should house the VCV and common historic market data

### File Structure

```
-app.py
-dashapp.py
-pages
  | -- portfolio_metrics.py
  | -- single_ticker.py
-objects
  | -- portfolio.py
  | -- securities.py
  | -- simgen.py
  | -- market_data.py
```

## #Current Features

- Query an individual stock
  - See the past 5 YR candlestick chart
  - See a Monte Carlo simulated vs Historic price distribution
  - View distribution stats
    - Value at Risk for individual stock
    - Annualized vol
    - Annualized Expected Return
    - Simply Weighted/ Exponentially Weighted
  - Variable lookback period
  - Variable sample size
- User upload stock portfolio
  - Mark at current price
  - Calculate portfolio weights

### Future Features

- Expected Return / Variance / Distrubtion
- Beta to selected market
  - S\&P 500
  - Russel 5000
  - Selected ETF
- User selection of MonteCarlo Method
- Option Pricing for individual stock
- Forward looking PDF for Portfolio returns
  - Basian modeling
  - ARIMA
- Backtesting tool - common trading strategies
  - "Buy and Hold"

## License

This project is licensed under the the MIT License - see the LICENSE.md file for details
