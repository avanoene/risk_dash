# risk_dash

Thesis Proposal: First create an object framework to handle a portfolio of assets, then create a risk application that uses that framework to calculate and display common risk factors and metrics, including: Value at Risk, Expected Portfolio Return and Volatility, Optimal Portfolio weights, Current Return, Systematic risk (Fama - French / CAPM)

To accomplish this task, I am planning on using current research and python packages to deliver a stable user experience. I am planning on using [Dash by Plotly](https://plot.ly/dash/) to create the front end user interface and deploying the underlying Flask app on either [DigitalOcean](https://www.digitalocean.com/) or [Heroku](https://www.heroku.com/)

The object model is housed in `~/objects/` where as the application pages are in `~/pages/` and are managed by `/dashapp.py` 

Needed dependencies:

```
dash
dash_html_components
dash_core_components
dash.dependencies
plotly
pandas
quandl
json
numpy
scipy
```
All should be availble with a `pip install`

To run:

First add file `apiconfig.py` to the directory at the same level as `dashapp.py`. That file should contain all of the api information to source the market data. I'm using [Quandl](https://www.quandl.com/) so my `apiconfig.py` file is the following:

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

quandl_apikey = 'quandl-api-key-replace-with-valid-key'
```

To use a different market data source, first write a specific `MarketData` class in `market_data.py`

To run the server locally, run the following command:

```
python dashapp.py
```

## Object Model

- Portofolio
  - Security
- SimulationGenerator
- MarketData

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

What I'm planning on doing is using the Portfolio object as a collection of Security objects
- This then should house the VCV and common historic market data

## File Structure

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

## Current Features

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

## Future Features

- User upload stock portfolio
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
