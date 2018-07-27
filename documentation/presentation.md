% risk_dash
% Alexander van Oene
% July 27, 2018

# Overview

- Portfolio Data
- Security Data
- Risk and Parameterized Metrics
- Simulation
- Live Demo
- Summary
- Questions

# Business problem

- New traded security or asset class
- Effect of an asset in the aggregate portfolio
- Speed

# Motivation

- Computational Python
    - numpy
    - pandas
    - scipy
    - statsmodels
- Frameworks in Python
    - flask
    - django
    - dash
- Risk Software
    - pyfolio
    - risk_dash

# risk_dash

- A frame work with common methods and interactions to formalize the data flow associated with a portfolio of traded assets

# How does risk_dash accomplish this task

- Wrapper classes to more efficient data structures
    - Generic classes that have defined methods and attributes
- Modeling logic
    - Value functions
- Applied methodology
    - Forecasting
    - Calculating standard metrics

# Data Streams

- Portfolio Data
- Security/Asset Data
    - Market Data (Prices/Price Action)
    - Fundamental Data

# Package Structure

- risk_dash.securities
- risk_dash.market_data
- risk_dash.simgen

# _Security Methods

- `valuation`
- `mark_to_market`
- `get_marketdata`
- `simulate`

# _MarketData Methods

- `gather`
- `current_price`
-

# Common Risk Metrics

- VaR (Distribution)
- Draw Down
- Portfolio Contribution
