
# risk_dash Dash application documentation

- [risk_dash Dash application documentation](#risk_dash-dash-application-documentation)
  - [Overview](#overview)
  - [Getting Started - Locally Running the Dash App](#getting-started---locally-running-the-dash-app)
    - [Dash applications](#dash-applications)
    - [The risk_dash Dash object](#the-risk_dash-dash-object)
    - [Running the application locally](#running-the-application-locally)
  - [Application Usage](#application-usage)
    - [Individual Equity Analysis Page - single_ticker.py](#individual-equity-analysis-page---single_tickerpy)
    - [Portfolio Metrics - portfolio_metrics.py](#portfolio-metrics---portfolio_metricspy)
  - [Summary](#summary)

## Overview

The included [Dash](https://dash.plotly.com/) application is purely to demonstrate a use case for the `risk_dash` package. There is minimal css provided through using [Bootstrap](https://getbootstrap.com/docs/4.0/getting-started/introduction/) and the [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) python library. For a complete overview of Dash, please check the respective documentation, as this will be very high level and explain the basics of how the sample application works.


## Getting Started - Locally Running the Dash App

### Dash applications 

To quote the [Dash](https://dash.plotly.com/introduction) documentation:

> Dash is a productive Python framework for building web analytic applications. 
> Written on top of Flask, Plotly.js, and React.js, Dash is ideal for building data visualization apps with highly custom user interfaces in pure Python. It's particularly suited for anyone who works with data in Python.

Due to it's lightweight nature and pure python syntax, it's a great use case to show off the functionality of the `risk_dash` framework. Dash applications are typically single purpose and leverage `plotly.js` for it's graphic capabilities. This application is structured in a way to have multiple pages using JavaScript callback functionality. These pages are rendered in the `app.layout` found in `dashapp.py`, then when an HTTP request is then made to the `Flask` server, the application's callback structure then updates the HTML Div container on the main index page and renders the according webpage. Each HTML and interactive object is referenced by it's `id` attribute, so each callback uses those references to pass along data and respond interactively. For this Dash application, the main callback function is taking the individually described page layouts and displaying them in the main `Div` container.

For example, from `dashapp.py`:

```python
@app.callback(
    Output('page_content', 'children'),
    [Input('url', 'pathname')]
)
def get_layout(url):
    if url != None:
        if url == '/portfolio':
            return(portfolio_metrics.layout)
        elif url == '/single':
            return(single_ticker.layout)
        elif url == '/docs':
            return(dcc.Markdown(docs))
        else:
            return(dcc.Markdown(readme))

```

The function takes the URL given as input, then returns the respective HTML object to populate the children attribute of the `page_content` `Div`-like object in the main `app.layout`. The decorator `@app.callback` registers this function with the `app Dash` object, explained [below](#the-risk_dash-dash-object). 

Since one of the objects of the `risk_dash` framework is to create an in memory risk valuation engine, this included app has two main pages:

- Individual Equity Analysis `single_ticker.py`
  - Shows how the `_Security` and `_MarketData` can be used to value a single security and run a Monte Carlo simulation
- Portfolio Dashboard `portfolio_metrics.py`
  - Shows how the `Portfolio` object can value a collection of `_Security` objects

As seen above, the URL ending in /portfolio/ returns the `portfolio_metrics.layout` member, the /single returns the `single_ticker.layout` member, /docs returns an HTML version of the getting started documentation, and any other URL returns the README.

The file structure of the app is as follows with a bit more detail than the README.md:

```
-app.py # contains server level configurations
-dashapp.py # contains application level routing and main structure
-pages # the layout rendering and callback functions to create each page
  | -- portfolio_metrics.py # displays a portfolio level risk
  | -- single_ticker.py # displays a single equity position risk
-objects # risk_dash framework objects
  | -- securities.py # security objects
  | -- simgen.py # simulation objects
  | -- market_data.py # market data objects
```

To add a page to the application, the process is simple:

- Create a `.py` file that contains the following:
  - A `dash_html_components.Div` object to replace the children of the `app.layout#page_content` named `layout`
  - The respective callback functions to populate the content of the `dash_html_components.Div` and register them with the `app.app` object
- In the `dashapp.py` file, register the desired URL in the `get_layout` function and return the `layout` member of the created `.py` file

### The risk_dash Dash object

Referring from the [Dash](https://dash.plotly.com/) documentation and source code, the Dash object handles all of the rendering of the JavaScript and HTML components of our defined application. This object is defined in `app.py`, where we define a couple of server level configurations. Here are the important definitions below:

```python
import dash
import dash_bootstrap_components as dbc

style_sheets = [dbc.themes.BOOTSTRAP] #add in the css stylesheets for Bootstrap
app = dash.Dash(__name__, external_stylesheets=style_sheets,) # main application initialization

server = app.server # exposing the underlying Flask server
app.config.suppress_callback_exceptions = True # configuration to suppress exceptions relating to the multi-page configuration 
```

The defined `app` object is the `Dash` instance that will need to register all of the defined callbacks we create. The `server` object is the underlying `Flask` server instance that hosts and interacts with the incoming HTTP requests. After defining these, we then import them to the `dashapp.py` file that will define the main, application level, functionality.

```python
# dash dependencies/modules
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# application level code
from app import app, server
from pages import single_ticker, portfolio_metrics
# ...

# the main application layout, defines the NavBar and the container that will store the rendered HTML from pages
app.layout = dbc.Container(
# ...
)

# if this is run as a script, then run the server
if __name__ == '__main__':
    print('Running')
    app.run_server()
```

When this script is then run with `python dashapp.py` or otherwise, all of the namespaces are loaded in, thus the Dash object registers the defined callbacks with the associated component inputs and HTML outputs and is ready to receive HTTP requests.

Next, we'll briefly talk about how to run the server locally, though it could be deployed on a remote server and receive HTTP requests over the broader internet.

### Running the application locally

To run the server locally using the underlying Flask Server, run the following command:

```
python dashapp.py
```

This runs the file as a script, loads in the necessary namespaces, and calls the `app.run_server()` method. Additonally, since the `Flask` app isn't intended to be a production server, in a production environment we might want to use `gunicorn` to run the server. We would just run `gunicorn dashapp:server` from the command line instead. Running the server with the `Flask` app locally for testing and proof of concept, calling `python dashapp.py` will run the server on the default port/local ip address, http://127.0.0.1:8050/, where you can then open the application in a web browser like Chrome.

## Application Usage

### Individual Equity Analysis Page - single_ticker.py

The intent for this page is to show the functionality of the `_MarketData` and `Equity` classes, with a simple data query and simulation run. The page is configured to run a Naive Monte Carlo simulation with a normal random walk, and a historic price simulation for comparison. The user puts in the ticker they want to evaluate, then the server calls the following callbacks:

- `get_data`
  - Creates a MarketData object by calling the Quandl API for a given stock ticker from the `dash_core_components.Input` labeled 'stock' and is called when the user hits the button labeled 'Run'
  - Creates a simulation object from the MarketData and computes a simulation and evaluates some metrics to be used later
  - Stores the data in hidden `<div>` as a json object
- `chart`
  - Takes the queried MarketData, appends  the forward steps of the configured Monte Carlo simulation and plots it as a time series
- `monte_carlo_histogram`
  - Takes the evaluated simulation data and plots it as a histogram
- `summary_table`
  - Takes the evaluated metrics and displays them as a HTML table

Here is a screenshot of the output from the `get_data`, `chart`, `monte_carlo_histogram`, and `summary_table` call backs

![Time Series plot for AAPL Adjusted Closing Prices](./aapl_marketdata.png)

![Histogram plot for AAPL Monte Carlo Simulation](./aapl_montecarlo_dist.png)

Again, the HTML layout is defined by the defined layout object, that contains the `dash` components to render the HTML and JavaScript as needed. In the future, this could be extended 

### Portfolio Metrics - portfolio_metrics.py

The intent for this page is to show the functionality of the `Portfolio` class, which is a collection of `Equity` object instances. An extension of this project could be to extend the object and run independent and correlated simulations as described in the [getting started docs](gettingstarted.rst##parametrically-calculating-the-value-at-risk). The user uploads a portfolio from a csv file, then the page pulls all the required data and evaluates the current value of the portfolio. When uploaded, the following callbacks are called:

- `output_upload`
  - When a portfolio csv is uploaded, then a `Portfolio` object is created and the underlying market data is queried. 
- `displayport`
  - Once the data is queried and stored, some simple metrics are calculated and displayed in the HTML table

Here is a screenshot of the upload element

![Portfolio Upload and Template Download](./portfolio_upload.png)

Here is the sample portfolio found in './portfolio_example.csv'

![HTML Table with Theoretical Portfolio Valuation](./portfolio_valuation.png)

## Summary

This lightweight application is not intended to be the only use of the `risk_dash` framework, but to show the initial possibilities of using an in memory risk engine that is lightweight enough to value simple and complex securities.