.. _gettingstarted:
 
.. role:: math(raw)
   :format: html latex
..

risk\_dash
==========

-  `Overview <#overview>`__
-  `Getting Started <#getting-started>`__

   -  `Security data, \_Security objects, and creating Security
      Subclasses <#security-data-security-objects-and-creating-security-subclasses>`__
   -  `Portfolio Data and creating a
      Portfolio <#portfolio-data-and-creating-a-portfolio>`__
   -  `Calculating Risk Metrics and Using the Portfolio
      Class <#calculating-risk-metrics-and-using-the-portfolio-class>`__

      -  `Mark the Portfolio <#mark-the-portfolio>`__
      -  `Parametrically Calculating the Value at
         Risk <#parametrically-calculating-the-value-at-risk>`__

   -  `Simulating the Portfolio <#simulating-the-portfolio>`__

      -  `Simulating a Unit Resolution
         Distribution <#simulating-a-unit-resolution-distribution>`__
      -  `Simulating a Path
         Distribution <#simulating-a-path-distribution>`__

   -  `Summary <#summary>`__

Overview
--------

`risk\_dash <https://github.com/avanoene/risk_dash>`__ is a framework to
help simplify the data flow for a portfolio of assets and handle market
risk metrics at the asset and portfolio level. If you clone the source
`repository <https://github.com/avanoene/risk_dash>`__, included is a
`Dash <https://plot.ly/dash/>`__ application to be an example of some of
the uses for the package. To run the Dash app, documentation is
`here <dashdocumentation.html>`__

Installation
------------

Since the package is in heavy development, to install the package fork
or clone the `repository <https://github.com/avanoene/risk_dash>`__ and
run ``pip install -e risk_dash/`` from the directory above your local
repository.

To see if installation was successful run
``python -c 'import risk_dash; print(*dir(risk_dash), sep="\n")'`` in
the command line, currently the output should match the following:

.. code:: bash

    $ python -c 'import risk_dash; print(*dir(risk_dash), sep="\n")'
    __builtins__
    __cached__
    __doc__
    __file__
    __loader__
    __name__
    __package__
    __path__
    __spec__
    market_data
    name
    securities
    simgen

Getting Started
---------------

Now that we have the package installed, let's go through the object
workflow to construct a simple long/short equity portfolio.

High level, we need to specify:

1. Portfolio Data

   -  We need to know what's in the portfolio

      -  Portfolio weights
      -  Types of Assets/Securities

2. Security data

   -  We need to know what is important to financially model the
      security

      -  Identification data: Ticker, CUSIP, Exchange
      -  Security specific data: expiry, valuation functions
      -  Market data: Closing prices, YTM

3. Portfolio/security constructors to handle the above data

To visualize these constructors, the below chart shows how the data will
sit:

|image0|

To do so, we'll need subclasses for the `\_Security <#security>`__ and
`\_MarketData <buildingclasses.html>`__ classes to model specific types
of securities. Currently supported is the Equity subclass. Once we have
the portfolio constructed, we will specify and calculate parameters to
simulate or look at historic distributions. We'll then create a subclass
of `\_Simulation <#simulation>`__ and `\_RandomGen <#randomgen>`__

Security data, ``_Security`` objects, and creating Security Subclasses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core of the package is in the ``_Security`` and ``Portfolio``
objects. ``Portfolio`` objects are naturally a collection of Securities,
however we want to specify the type of securities that are in the
portfolio. Since we're focusing on a long/short equity portfolio we want
to create an Equity subclass.

Subclasses of ``_Security`` classes must have the following methods:

-  valuation(current\_price)
-  mark\_to\_market(current\_price)
-  get\_marketdata()

In addition, we want to pass them the associated ``_MarketData`` object
to represent the security's historic pricing data. To build the
``Equity`` subclass, we first want to inherit any methods from the
``_Security`` class:

.. code:: python

    class Equity(_Security):

        def __init__(
                self,
                ticker,
                market_data : md.QuandlStockData,
                ordered_price,
                quantity,
                date_ordered
            ):
            self.name = ticker
            self.market_data = market_data
            self.ordered_price = ordered_price
            self.quantity = quantity
            self.initial_value = ordered_price * quantity
            self.date_ordered = date_ordered
            self.type = 'Equity'

To break down the inputs, we want to keep in mind that the goal of this
subclass of the \_Security object is to provide an interface to model
the Equity data.

-  ticker is going to be the ticker code for the equity, such as 'AAPL'
-  market\_data is going to be a subclass of the \_MarketData object
-  ordered\_price is going to be the price which the trade occurred
-  quantity for Equity will be the number of shares
-  date\_ordered should be the date the order was placed

.. note:: Currently the implemented \_MarketData subclass is
    QuandlStockData, which is a wrapper for `this Quandl dataset
    api <https://www.quandl.com/databases/WIKIP>`__. This data is no
    longer being updated, for current market prices you must create a
    \_MarketData subclass for your particular market data. Information
    to construct the subclass is on `Building Custom
    Classes <buildingclasses.html>`__.

Required Inputs at the \_Security level are intentionally limited, for
example if we wanted to create a class for Fixed Income securities, we
would want more information than this Equity subclass. An example Bond
class might look like this:

.. code:: python

    class Bond(_Security):
        def __init__(
                self,
                CUSIP,
                market_data,
                expiry,
                coupon,
                frequency,
                settlement_date,
                face_value
            ):
            self.name = CUSIP
            self.market_data = market_data
            self.expiry = expiry
            self.coupon = coupon
            self.frequency = frequency
            self.settlement_date = settlement_date
            self.face_value = face_value
            self.type = 'Bond'

Similarly to the Equity subclass, we want identification information,
market data, and arguments that will either help in calculating
valuation, current returns, or risk measures.

Returning to the Equity subclass, we now need to write the valuation and
mark to market methods:

.. code:: python

    class Equity(_Security):
      # ...
      def valuation(self, price):
          value = (price - self.ordered_price) * self.quantity
          return(value)

      def mark_to_market(self, current_price):
          self.market_value = self.quantity * current_price
          self.marked_change = self.valuation(current_price)
          return(self.marked_change)

For linear instruments such as equities, valuation of a position is just
the price observed minus the price ordered at the size of the position.
``valuation`` is then used to pass a hypothetical price into the
valuation function, in this case (Price - Ordered) \* Quantity, where as
``mark_to_market`` is used to pass the current EOD price and mark the
value of the position. This is an important distinction, if we had a
nonlinear instrument such as a call option on a company's equity price,
the valuation function would then be:

.. math::


   Value = min\{0, S_{T} - K\}

Where :math:`S_{T}` is the spot price for the equity at expiry and
:math:`K` is the agreed strike price. Valuation also is dependent on
time for option data, however if you were to use a binomial tree to
evaluate the option, you would want to use this same value function and
discount the value a each node back to time=0.

Our mark to market then would need to make the distinction between this
valuation and the current market price for the call option. The mark
would then keep track of what the current market value for the option to
keep track of actualized returns.

The final piece to creating the Equity subclass is then to add a
``get_marketdata()``\ method. Since we just want a copy of the reference
of the ``market_data``, we can just inherit the ``get_marketdata()``
from the \_Security class.

The Equity subclass is already implemented in the package, we can create
an instance from ``risk_dash.securities``. Let's make an instance that
represents an order of 50 shares of AAPL, Apple Inc, at close on March
9th, 2018:

.. code:: python

    >>> from risk_dash.market_data import QuandlStockData
    >>> from risk_dash.securities import Equity
    >>> from datetime import datetime
    >>> apikey = 'valid-quandl-apikey'
    >>> aapl_market_data = QuandlStockData(
      apikey = apikey,
      ticker = 'AAPL'
    )
    >>> aapl_stock = Equity(
      ticker = 'AAPL',
      market_data = aapl_market_data,
      ordered_price = 179.98,
      quantity = 50,
      date_ordered = datetime(2018,3,9)
    )
    >>> aapl_stock.valuation(180.98) # $1 increase in value
    50.0
    >>> aapl_stock.mark_to_market(180.98) # Same $1 increase
    50.0
    >>> aapl_stock.market_value
    9049.0
    >>> aapl_stock.marked_change
    50.0
    >>> vars(aapl_stock)
    {'name': 'AAPL',
     'market_data': <risk_dash.market_data.QuandlStockData at 0x1147c2668>,
     'ordered_price': 179.98,
     'quantity': 50,
     'initial_value': 8999.0,
     'date_ordered': datetime.datetime(2018, 3, 9, 0, 0),
     'type': 'Equity',
     'market_value': 9049.0,
     'marked_change': 50.0}

As we can see ``aapl_stock`` now is a container that we can use to
access it's attributes at the Portfolio level.

.. note:: Another important observation is that the Equity subclass will
    only keep a reference to the underlying QuandlStockData, which will
    minimize duplication of data. However, at scale, you'd want minimize
    price calls to your data source, you could then do one call at the
    Portfolio level then pass a reference to that market\_data at the
    individual level. Then your Equity or other \_Security subclasses
    can share the same \_MarketData, you would then just write methods
    to interact with that data.

Now that we have a feeling for the \_Security class, we now want to
build a Portfolio that contains the \_Security instances.

Portfolio Data and creating a Portfolio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To iterate on what we said before, an equity position in your portfolio
is represented by the quantity you ordered, the price ordered at, and
when you ordered or settled the position. In this example, we'll use the
following theoretical portfolio found in ``portfolio_example.csv``:

+----------+----------+-----------------+----------------+------------+
| Type     | Ticker   | Ordered Price   | Ordered Date   | Quantity   |
+==========+==========+=================+================+============+
| Equity   | AAPL     | 179.98          | 3/9/18         | 50         |
+----------+----------+-----------------+----------------+------------+
| Equity   | AMD      | 11.7            | 3/9/18         | 100        |
+----------+----------+-----------------+----------------+------------+
| Equity   | INTC     | 52.19           | 3/9/18         | -50        |
+----------+----------+-----------------+----------------+------------+
| Equity   | GOOG     | 1160.04         | 3/9/18         | 5          |
+----------+----------+-----------------+----------------+------------+

With this example, the portfolio is static, or just one snap shot of the
weights at a given time. In practice, it might be useful to have
multiple snapshots of your portfolio, one's portfolio would be changing
as positions enter and leave thus having a time dimensionality. The
Portfolio class could be easily adapted to handle that information to
accurately plot historic performance by remarking through time. This
seems more of an accounting exercise, risk metrics looking forward would
probably still only want to account for the current positions in the
portfolio. Due to this insight, the current Portfolio class only looks
at one snap shot in time.

With a portfolio so small, it is very easily stored in a csv and each
security can store the reference to the underlying market data
independently. As such, there is an included portfolio constructor
method in the portfolio class from csv, ``construct_portfolio_csv``:

.. code:: python

    >>> from risk_dash.securities import Portfolio
    >>> current_portfolio = Portfolio()
    >>> port_dict = current_portfolio.construct_portfolio_csv(
      data_input='portfolio_example.csv',
      apikey=apikey
    )
    >>> vars(current_portfolio)
    {'port': {'AAPL Equity': <risk_dash.securities.Equity at 0x11648b5c0>,
      'AMD Equity': <risk_dash.securities.Equity at 0x116442c50>,
      'INTC Equity': <risk_dash.securities.Equity at 0x1177b75c0>,
      'GOOG Equity': <risk_dash.securities.Equity at 0x1177bc390>}}
    >>> vars(current_portfolio.port['AMD Equity'])
    {'name': 'AMD',
     'market_data': <risk_dash.market_data.QuandlStockData at 0x11648b2e8>,
     'ordered_price': 11.699999999999999,
     'quantity': 100,
     'initial_value': 1170.0,
     'date_ordered': '3/9/18',
     'type': 'Equity'}

At this moment, the ``current_portfolio`` instance is only a wrapper for
it's port attribute, a dictionary containing the securities in the
Portfolio object. Soon we'll use this object to mark the portfolio,
create a simulation to estimate value at risk, look at the covariance
variance matrix to calculate a parameterized volatility measure, and
much more.

The ``Portfolio`` class handles interactions with the portfolio data and
the associated securities in the portfolio. If you have a list of
securities you can also just pass the list into the Portfolio instance.
The following code creates a portfolio of just the AAPL equity that we
created earlier:

.. code:: python

    >>> aapl_portfolio = sec.Portfolio([aapl_stock])
    >>> vars(aapl_portfolio)
    {'port': {'AAPL Equity': <risk_dash.securities.Equity at 0x1164b2e80>}}

If we want to add a security to this portfolio, we can call the
``add_security`` method, to remove a security we call the
``remove_security`` method:

.. code:: python

    >>> amd_market_data = QuandlStockData(
      ticker='AMD',
      apikey=apikey
    )
    >>> amd_stock = Equity(
      ticker = 'AAPL',
      market_data = amd_market_data,
      ordered_price = 11.70,
      quantity = 100,
      date_ordered = datetime(2018,3,9)
    )
    >>> aapl_portfolio.add_security(amd_stock)
    >>> aapl_portfolio.port
    {'AAPL Equity': <risk_dash.securities.Equity at 0x1164b2e80>,
     'AMD Equity': <risk_dash.securities.Equity at 0x11791cc88>}
    >>> aapl_portfolio.remove_security(amd_stock)
    >>> aapl_portfolio.port
    {'AAPL Equity': <risk_dash.securities.Equity at 0x1164b2e80>}
    >>> aapl_portfolio.remove_security(aapl_stock)
    >>> aapl_portfolio.port
    {}

Calculating Risk Metrics and Using the Portfolio class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have our ``Portfolio`` constructed with the securities we
have on the book let's use the class to calculate some market risk
metrics.

Mark the Portfolio
^^^^^^^^^^^^^^^^^^

Let's first mark the current portfolio. Since we want to know the
current value of the portfolio, the mark method will calculate the value
of the portfolio at the current price for each security. The current
price is going to be the last known mark, the price at the closest date
to today.

.. note:: Since the QuandlStockData source hasn't been updated since
    3/27/2018, we would expect the last shared date to be 3/27/2018.
    However, you should use the last shared date as a flag to see if an
    asset's \_MarketData isn't updating. With certain assets, such as
    Bonds or illiquid securities, marking daily might not make as much
    sense, so common shared date doesn't mean as much.

.. code:: python

    >>> current_portfolio.mark()
    >>> vars(current_portfolio)
    {'port': {'AAPL Equity': <risk_dash.securities.Equity at 0x10f8b2940>,
      'AMD Equity': <risk_dash.securities.Equity at 0x1a1f6b0908>,
      'INTC Equity': <risk_dash.securities.Equity at 0x110538d30>,
      'GOOG Equity': <risk_dash.securities.Equity at 0x110548e10>},
     'market_change': -1476.6999999999989,
     'marked_portfolio': {'AAPL Equity': (8999.0, 8417.0),
      'AMD Equity': (1170.0, 1000.0),
      'INTC Equity': (-2609.5, -2559.5),
      'GOOG Equity': (5800.1999999999998, 5025.5)},
     'date_marked': Timestamp('2018-03-27 00:00:00'),
     'initial_value': 13359.700000000001}

The ``mark`` method now creates the ``marked_portfolio`` dictionary that
stores a tuple, (initial\_value, market\_value), for every security in
the portfolio. We also now can calculate a quick holding period return,
``holdingreturn = (current_portfolio.initial_value + current_portfolio.market_change)/current_portfolio.initial_value``

.. code:: python

    >>> holdingreturn = (current_portfolio.market_change)/current_portfolio.initial_value
    >>> print(holdingreturn)
    -0.11053391917483169

This hypothetical portfolio apparently hasn't performed over the month
since inception, it's lost 11%, but let's look at historic returns
before we give up on the portfolio. We can call ``portfolio.quick_plot``
to look at a ``matplotlib`` generated cumulative return series of the
portfolio. If you wanted more control over plotting, you could use the
returned
``pandas DataFrame. In fact, the current implementation is just using the``\ pandas
DataFrame\ ``method``\ plot()\`:

.. code:: python

    >>> marketdata = current_portfolio.quick_plot()

.. figure:: quick_plot_image.png
   :alt: quick\_plot() Output

   quick\_plot() Output

Parametrically Calculating the Value at Risk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As we can see, this portfolio is pretty volatile, but has almost doubled
over the last four years. Let's calculate what the portfolio daily
volatility over the period based off the percent change by calling
``get_port_volatility`` using ``percentchange`` from the
``market_data``:

.. code:: python

    >>> variance, value_at_risk = current_portfolio.set_port_variance(
      key = 'percentchange'
    )
    >>> volatility = np.sqrt(variance)
    >>> print(volatility)
    0.01345831069378136
    >>> mean = np.mean(current_portfolio.market_data['portfolio'])
    >>> print(mean)
    0.0007375242310493472

We calculated 1.3% daily standard deviation or daily volatility, if the
distribution is normally distributed around zero, then we would expect
that 95% of the data is contained within approximately 2 standard
deviations. We can visually confirm, as well as look to see if there are
other distributional aspects we can visually distinguish:

.. code:: python

    >>> import matplotlib.pyplot as plt
    >>> marketdata['portfolio'].plot.hist(bins=20,title='Portfolio Historic Returns')
    >>> plt.axvline(temp * 1.96, color='r', linestyle='--') # if centered around zero, then
    >>> plt.axvline(-temp * 1.96, color='r', linestyle='--') #

.. figure:: portfolio_returns.png
   :alt: Portfolio Returns

   Portfolio Returns

This distribution looks highly centered around zero, which could signal
kurtosis. This seems indicative of equity data, especially for daily
returns. Right now, a good place to start thinking about metric
parameterization is to assume normality and independence in daily
returns. While this assumption might not be very good or might vary
between security to security in the portfolio, which we can account for
in simulation or purely using historic returns to calculate risk
metrics, we can use this distribution assumption to quickly get a Value
at Risk metric over a time horizon.

The default time horizon is 10 days at a 95% confidence level for the
``set_port_variance`` method, so if we look at the returned
``value_at_risk``:

.. code:: python

    >>> print(value_at_risk)
    -0.083413941112170473

This value is simply the standard deviation scaled by time, at the
critical value specified:

.. math::


   VaR_{t, T} = \sigma \cdot \sqrt{T-t} \cdot Z^{*}_{p = \alpha}

We can interpret this Value at Risk as being the lower bound of the 95%
confidence interval for the 10 day distribution. For this portfolio, a
loss over 10 days less than 8.3% should occur 2.5% of the time, on
average. To get the dollar value of the 10 Day Value at Risk, we would
just multiply this percent change by the current portfolio market value.

.. code:: python

    >>> dollar_value_at_risk = value_at_risk * (current_portfolio.initial_value + current_portfolio.marked_change)
    >>> print(dollar_value_at_risk)
    -991.20786223592188

Similarly, we could interpret as over the a 10 day period, on average,
2.5% of the time there could be an approximate loss over $991.21 dollars
for this portfolio. However, this is relying on the assumption that the
portfolio is: a) normally distributed, and b) daily returns are serially
independent and identically distributed. One way we can go around this
is to look at the historic distribution

.. code:: python

    >>> historic_distribution, historic_var = current_portfolio.historic_var()
    >>> print(historic_var)
    -0.073051970330112487

This is calculated by doing a cumulative sum of returns over each
horizon time period, then taking the appropriate percentile of the
distribution to get a VaR based on historic prices. This is is smaller
than the parametric VaR due to the fact that the distribution looks more
right skewed as shown below

.. figure:: historic_10_return.png
   :alt: Historic 10D VaR

   Historic 10D VaR

This method is fairly simple, however it is based on the assumption that
the previous distribution of outcomes is a good representation of the
future distribution.

Another way we've implemented to calculate the value at risk is to
simulate the portfolio distribution.

Simulating the Portfolio
~~~~~~~~~~~~~~~~~~~~~~~~

When simulating portfolio returns, one's objective is to correctly
specify the portfolio distribution. I consider two major approaches,
"bottom-up" and "top-down".

The "bottom-up" approach would include simulating the underlying
securities first and then valuing the portfolio through the simulated
distributions. The major strength of this method is the ability to
easily value the effect of derivative securities on the portfolio. Since
one would simulate the derivative's underlier, you could easily then
apply the associated value function through the simulated distribution
to get the security's profit and loss distribution. Another benefit to
this methodology is the analyst has the freedom to change the simulation
process at a security level. General Brownian motion might be a good
assumption for long/short equity positions, but maybe not as good when
simulating yield curves for bonds. Another strength would be the ability
to change portfolio weights of securities post simulation, if you
simulate a base unit of the security you could then scale the weights
accordingly to easily reweigh the portfolio. The biggest challenge to
this methodology is to ensure that each simulation value represents the
same market environment, meaning that each simulation pull represents
the same environment state. While you can potentially do a convolution
of the different simulations to get a representative joint distribution
of the portfolio, you must ensure that one is capturing the covariance
between the securities. For example, equities and bonds have
historically had negative correlation to each other, thus a portfolio
containing both would potentially have a lower variance than each
security separate. To capture that in a simulation one would have to
simulate directly from the variance-covariance matrix or do a
convolution to combine separate simulations together. While both are
possible, and in practice it is probably a preferred methodology,
however it's not within the scope of this project.

The "top-down" approach would include aggregating the portfolio a priori
and then simulating that distribution. Since the portfolio is made of
the member securities, thus the aggregated distribution represents all
covariance. While this method gets a little be trickier to handle with
derivative securities, since you would need historic market prices per
contract and potentially roll adjust through the time period, for
securities like equities the assumption seems arguable. The benefit of
this method would be having to deal with one simulation and verifying if
it represents the underlying distribution vs having several different
simulations and verifying if they accurately represent the covariance of
constituent securities. The drawback is having less flexibility in the
modeling of individual securities within the portfolio. Another drawback
is to change the weighting or portfolio members, one must recombine and
simulate the new portfolio, which could be computationally intensive
depending on the methodology.

Either way, to implement simulation, the ``_Simulation`` and
``_RandomGen`` class that handle the calculation and generation
respectfully. For example, to implement a naive return model, the
included ``NaiveMonteCarlo`` class represents the following generation
function for a single observation:

.. math::


   R_{t} = \phi

Where :math:`\phi` representing a pull from an imposed distribution. As
such, we need to specify that imposed distribution, thus we include the
``NormalDistribution _RandomGen`` class to generate a pull. This class
is just a wrapper to for numpy.random.normal with the mean and standard
deviation specified in the initialization.

Since the aim is to specify the portfolio distribution X days into the
future, we want to simulate a cumulative return path through time. Under
the assumption that each day is independent, the individual simulation
path is then:

.. math::


   P = \sum_{t=1}^{X} R_{t} = \sum_{t=1}^{X} \phi

Now to fully specify the distribution via a Monte Carlo process, we will
generate :math:`Y` paths to represent the underlying :math:`X` day
distribution. To get the mean of the distribution at each :math:`t` step
from 1 to :math:`X`:

.. math::


   E(R_{t}) = \frac{1}{Y} \sum_{i=1}^{Y} P_{t, i} + E((R_{t-1}))

To get the variance:

.. math::


   Var(R_{t}) = E\left(\left(R_{t} - E(R_{t})\right)^{2}\right) + Var(R_{t}) = \frac{1}{Y^{2}} \sum_{i=1}^{Y}\left(P_{t,i} - \bar{P_{t}} \right)

Since each return is assumed independently and identically distributed,
the above condenses to:

.. math::


   Var(R_{t}) = t \cdot Var(R_{t})

Since we can now switch out the distribution of :math:`\phi` to
represent the portfolio or constituent securities, this generation
function is agnostic of which approach explained above is taken. It's
for that reason the design choice was made to make the ``_RandomGen``
and ``_Simulation`` classes seperate instead of building methods
directly into the ``Portfolio`` or ``_Security`` class.

Simulating a Unit Resolution Distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First let's simulate a unit resolution distribution. By default, the
resolution is one day, but depending on the market data resolution you
could simulate to match. Since the default is one day, let's simulate a
one day distribution and then simulate a X day forward path distribution
using ``aapl_stock``:

.. code:: python

    >>> from risk_dash.simgen import NormalDistribution, NaiveMonteCarlo
    >>> log_return_generator = NormalDistribution(
        location = aapl_stock.market_data.currentexmean,
        scale = aapl_stock.market_data.currentexvol
      )

Since we're just simulating one day, we can directly use the generator
object simulate a one day return distribution. With our new
``log_return_generator`` instance, we are assuming a normally
distributed return series. By default, using ``currentexmean`` will
center the distribution around the closest 80 day exponentially weighted
mean of daily AAPL returns. Similarly, using ``currentexvol`` will set
the standard deviation to the closest 80 day exponentially weighted
standard deviation of historic daily AAPL returns. To simulate one pull
now from a normal distribution, we have an observation that represents a
log return of AAPL.

.. code:: python

    >>> log_return_generator.generate(1)
    array([-0.00948158])

One observation isn't really helpful for us, we now want to simulate an
arbitrarily large amount of observations to converge to the underlying
distribution. In this case, let's simulate 5000 observations:

.. code:: python

    >>> import numpy as np
    >>> one_day_simluation = log_return_generator.generate(5000)
    >>> len(one_day_simulation)
    5000
    >>> np.mean(one_day_simluation)
    -0.00036139846164594291
    >>> aapl_stock.market_data.currentexmean
    -0.00040076765463907944
    >>>np.std(one_day_simulation)
    0.016497493178538599
    >>>aapl_stock.market_data.currentexvol
    0.016485817752205818

To parameterize the sampling distribution of the distribution, we can
simulate an arbitrarily large amount of simulations to converge to the
sampling distribution:

.. code:: python

    >>> multiple_one_day_simulations = np.array([log_return_generator.generate(5000) for i in 5000])
    >>> np.mean(np.mean(multiple_one_day_simulations, axis = 0)) # sampling distribution mean of the simulation mean
    -0.00039625427660093282
    >>> np.std(np.mean(multiple_one_day_simulations, axis=0))
    0.00023461080665209953
    >>> np.mean(np.std(multiple_one_day_simulations, axis=0))
    0.016484835778989758
    >>> np.std(np.std(multiple_one_day_simulations, axis=0))
    0.00016629650698145025

With the mean and standard deviation of the sampling distribution we can
construct confidence intervals to see if our calculated mean and
variance is contained. This would imply we have specified the imposed
distribution based on our calculation of ``currentexvol`` and
``currentexmean``. The calculation for a 95% confidence level is:

.. math::


   \bar{X} \pm Z^{*}_{p=\alpha} \frac{s}{\sqrt{n}}

So for this case, for a 95% confidence level, :math:`1-\alpha`, our
confidence interval for the simulation mean is (-0.0004027, -0.0003897)
and for the simulation standard deviation is (0.0164802, 0.0164894). Our
calculated historic values, -0.0004007 and 0.0164858, both fall within
those confidence intervals so at the 95% confidence level we can
determine this simulation represents a normally distributed one day
return series.

Simulating a Path Distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To simulate a forward return path of independent returns, we now want to
create a ``NaiveMonteCarlo`` object to simulate :math:`Y` forward
resolution paths.

.. code:: python

    >>> simulation_generator = NaiveMonteCarlo(log_return_generator)

The ``NaiveMonteCarlo`` accepts any ``_RandomGen`` object, so we could
potentially pass a ``_RandomGen`` object that might more accurately
represent our underlying data. For example, if we thought that AAPL was
distributed with a Cauchy distribution to capture fatter tails, we could
pass in a ``_RandomGen`` object that represented the distribution. Now
we'll maintain the assumption that the log returns are normally
distributed and use the ``generator`` instance we created earlier.

To simulate 5000 paths for a 5 day forward distribution, we would then
call the ``simulate`` method passing the arguments ``periods_forward=5``
and ``number_of_simulations=5000``. This will set the
``simulation_mean``, ``simulation_std``, and ``simulated_distribution``
attributes and return the simulated distribution.

.. code:: python

    >>> path_simulation = simulation_generator.simulate(periods_forward=5, number_of_simulations=5000)
    >>> path_simulation.shape
    (5000,5)
    >>> simulation_generator.simulation_mean
    array([-0.00050452, -0.00082389, -0.00105195, -0.00135753, -0.0019303 ])
    >>> simulation_generator.simulation_std
    array([ 0.01630096,  0.02311434,  0.0283451 ,  0.03211978,  0.03607576])

The simulation distribution now is 5000 individual 5 day paths,
represented as a ``numpy`` array of shape (5000,5). The
``simulation_mean`` and ``simulation_std`` are then calculated across
the column axis, giving us the simulated generation through time. Since
this method is fairly naive, essentially the cumulative sum of
independent random normals, it makes sense that the ``simulation_mean``
vector is essentially ``E(R_{t}) = t \cdot E(R_{t=1})`` and
``S.D.(R_{t}) = \sqrt{t} * S.D.(R_{t=1})``. If we wanted to implement a
more standard approach of simulating returns, we could then create a
``_Simulation`` class that would represent the value function. To
simulate the portfolio from the top down approach, we would then just
use the portfolio mean and variance to then simulate the portfolio.

Summary
~~~~~~~

While this is just the first introduction to the package, there are many
expandable directions to go. The aim for the package is to help
formalize the development process by providing clear template classes
and use cases. The next steps are to write ``_Security`` classes that
match the portfolio that the analyst is trying to model and
``_MarketData`` classes that match the specific data store for the
application.

.. |image0| image:: data:image/png;base64,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
