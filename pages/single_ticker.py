import json

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from app import app
from risk_dash import market_data as md, simgen as mc
from apiconfig import quandl_apikey as apikey


time_options =['5D',
'10D',
'20D',
'3M',
'6M',
'1Y',
'5Y',
'10Y'
]

layout = dbc.Container([
    html.H2('Individual Equity Analysis'),
    dbc.Row(
        [
            html.H5('Enter ticker symbol and hit Run to run simulation'),
            html.Label('Ticker'),
            dcc.Input(id='stock', value='AAPL', type='text'),
            html.Button(id='submit', n_clicks=0, children='Run')
        ],
    ),
    html.Div(id='querydata', style={'display':'none'}),
    html.Div(id='simdata', style={'display':'none'}),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='equityline', config=dict( autosizeable=True)), lg=12)
        ],
        align='center'
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.H5('Number of Simulations'),
                    dcc.Input(
                        id='obs',
                        type='number',
                        placeholder='Number of MC Obs',
                        value=1000
                    )
                ],
                md=2
            ),
            dbc.Col(
                [
                    html.H5('Lookback Period for Volatility Parameterization'),
                    dcc.RadioItems(
                        id='lookback',
                        options=[
                            {'label': 20, 'value': 20},
                            {'label': 80, 'value': 80},
                            {'label': 100, 'value': 100}
                        ],
                        value = 80,
                        labelStyle={'display': 'inline-block'}
                    )
                ],
                md=2
            ),
            dbc.Col(
                [
                    html.H5('Number of Days Forward'),
                    dcc.Input(
                        id='periods_forward',
                        type='number',
                        placeholder = 'Number of Days Forward',
                        value = 10
                    )
                ],
                md=2
            )
        ],
        align='center'
    ),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='montecarlo'),
            md=6
        ),
        dbc.Col(
            id='metrics_table',
            md=6
        )
        ],
    )
    ],
    fluid=True
)

@app.callback(
        Output('querydata', 'children'),
        [Input('submit', 'n_clicks')],
        [
            State('stock', 'value'),
            State('obs', 'value'),
            State('lookback', 'value'),
            State('periods_forward', 'value')
        ]
    )

def get_data(n_clicks,stock, obs, lookback, forward):
    if n_clicks != 0:
        data = md.QuandlStockData(apikey, stock, days=lookback)
        gen = mc.NormalDistribution(
            location = data.currentexmean,
            scale = data.currentexvol
        )
        sim = mc.NaiveMonteCarlo(
            gen,
            obs=obs
        )
        sim.simulate(forward, obs)
        dist = sim.simulated_distribution * data.current_price()
        hist_dist = (data.market_data['percentchange'] * data.current_price()).dropna()
        return json.dumps(
            {
                'data': data.market_data.to_json(date_format='iso', orient='records'),
                'dist': list(dist),
                'hist_dist': list(hist_dist),
                'currentvol': data.currentexvol,
                'currentexvol': data.currentexvol * np.sqrt(252),
                'currentswvol': data.currentswvol * np.sqrt(252),
                'currentexr': (1 + data.currentexmean) ** (252) - 1,
                'currentswr': (1 + data.currentswmean) ** (252) - 1,
                'percentVaR': np.nanpercentile(sim.simulated_distribution, 2.5),
                'forwardSimulationMean': list(np.exp(sim.simulation_mean) * data.current_price()),
                'forwardSimulationLower': list(np.exp(sim.simulation_mean - 2 * sim.simulation_std) * data.current_price()),
                'forwardSimulationUpper' : list(np.exp(sim.simulation_mean + 2 * sim.simulation_std) * data.current_price()),
                'currentprice': data.current_price()
            }
        )


@app.callback(
    Output('equityline', 'figure'),
    [
        Input('querydata', 'children'),
        Input('stock', 'value')
    ]
)
def chart(data, stock):
    data = json.loads(data)
    tempdata = pd.DataFrame(json.loads(data['data']))
    tempdata['date'] = pd.to_datetime(tempdata['date'])
    forward_dates = pd.bdate_range(
            tempdata['date'].max() + BDay(1) ,
            tempdata['date'].max() + BDay(len(data['forwardSimulationMean']))
    )
    line = go.Scatter(
        x = tempdata['date'],
        y = tempdata['adj_close'],
        name = stock + ' Adjusted Close Price'
    )
    average = go.Scatter(
        x = forward_dates,
        y = data['forwardSimulationMean'],
        name = 'Simulation Average'
    )
    lower_std = go.Scatter(
        x = forward_dates,
        y = data['forwardSimulationLower'],
        name = 'Simulation Lower Bound'
    )
    upper_std = go.Scatter(
        x = forward_dates,
        y = data['forwardSimulationUpper'],
        name = 'Simulation Upper Bound'
    )

    line_candle = go.Candlestick(x = tempdata['date'],
                          open=tempdata['adj_open'],
                          close = tempdata['adj_close'],
                          low=tempdata['adj_low'],
                          high=tempdata['adj_high'],
                          increasing=dict(
                              line=dict(
                                  color='black'
                                  )
                          ),
                          decreasing=dict(
                              line=dict(
                                  color='red'
                              )
                          ),
                          name= stock + ' Adjusted Price'
    )

    outlayout = dict(
        title = stock + ' Adjusted Prices',
        xaxis = dict(
            rangeselector=dict(
                buttons=list([
                    dict(
                        count=5,
                        label='5D',
                        step='day',
                        stepmode='backward'
                    ),
                    dict(
                        count=20,
                        label='20D',
                        step='day',
                        stepmode='backward'
                    ),
                    dict(
                        count=3,
                        label='3M',
                        step='month',
                        stepmode='backward'
                    ),
                    dict(
                        count=6,
                        label='6M',
                        step='month',
                        stepmode='backward'
                    ),
                    dict(
                        count=1,
                        label='YTD',
                        step='year',
                        stepmode='todate'
                    ),
                    dict(
                        count=1,
                        label='1Y',
                        step='year',
                        stepmode='backward'
                    ),
                    dict(
                        count=5,
                        label='5Y',
                        step='year',
                        stepmode='backward'
                    ),
                    dict(
                        step='all'
                    )
                ]
                ),
                visible=True
            )
        )
    )
    fig = go.Figure(data=[line, upper_std, average, lower_std], layout=outlayout)
    return fig


@app.callback(
    Output('montecarlo', 'figure'),
    [
        Input('querydata', 'children'),
        Input('periods_forward', 'value')
    ]
)
def monte_carlo_histogram(simdata, forward):
    simdata = json.loads(simdata)
    tempdata = pd.DataFrame(json.loads(simdata['data']))
    fig_data = [
        go.Histogram(
            x=simdata['dist'],
            histnorm='probability',
            opacity=.75,
            name='MC {}D Simulation'.format(forward)
        )
    ]
    fig_data.append(
        go.Histogram(
            x = tempdata['percentchange'].rolling(forward).sum() * simdata['currentprice'],
            histnorm='probability',
            opacity=.75,
            name='Historic {}D Distribution'.format(forward)
        )
    )
    layout = go.Layout(barmode='overlay')
    fig = go.Figure(data=fig_data, layout=layout)
    return fig


@app.callback(Output('metrics_table', 'children'),
              [Input('querydata', 'children'),
               Input('periods_forward', 'value')])
def summary_table(sim, forward):
    simdata = json.loads(sim)
    var = np.nanpercentile(simdata['dist'], 2.5)
    percentvar = simdata['percentVaR']
    percentvol = simdata['currentvol'] * 2
    actvar = np.nanpercentile(simdata['hist_dist'], 2.5)
    simvol = np.nanstd(simdata['dist'])
    exvol = simdata['currentexvol']
    swvol = simdata['currentswvol']
    exreturn = simdata['currentswr']
    ewexreturn = simdata['currentexr']
    metrics = [var, percentvar, actvar, percentvol, simvol, exvol, swvol, exreturn, ewexreturn]
    names = ['Simulated Dollar {}D Value at Risk'.format(forward),
             'Simulated Percent {}D VaR'.format(forward),
             'Historic Dist {}D VaR'.format(forward),
             'Historic {}D Percent VaR @ 2 SD'.format(forward),
             'Dollar SD Move',
             'Historic Exponentially Weighted Annualized Vol',
             'Historic Simply Weighted Annualized Vol',
             'Expected SW Annualized Return',
             'Expected EW Annualized Return'
             ]
    tbl_out = [html.Tr([
            html.Th(
                'Distribution Metric'
            ),
            html.Th(
            'Value'
            )
            ]
        )
    ]
    tbl_out = tbl_out + [html.Tr([html.Td(i), html.Td('{:.3f}'.format(j))])
                         for i , j in zip(names, metrics)]
    return html.Table(tbl_out, className='table')
