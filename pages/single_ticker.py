import json

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from app import app
from objects import market_data as md, simgen as mc
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

layout = html.Div([
    html.Label('Ticker'),
    dcc.Input(id='stock', value='AAPL', type='text'),
    html.Button(id='submit', n_clicks = 0, children='Query'),
    html.Div(id='querydata', style={'display':'none'}),
    html.Div(id='simdata', style={'display':'none'}),
    html.Div(
        [
            dcc.Graph(id='equityline')
        ],
        className='row'
    ),
    html.Div(
        [dcc.Input(
        id='obs',
        type='number',
        placeholder='Number of MC Obs',
        value=1000
        ),
        dcc.RadioItems(
            id='lookback',
            options=[
                {'label': 20, 'value': 20},
                {'label': 80, 'value': 80},
                {'label': 100, 'value': 100}
        ],
            value = 80,
            labelStyle={'display': 'inline-block'}
        )],
        className='row'
    ),
    html.Div([
        html.Div(
            dcc.Graph(id='montecarlo'),
            className='col-md-6'
        ),
        html.Div(
            id='metrics_table',
            className='col-md-6'
        )
        ],
        className='row'
    )
    ],
    className='container-fluid'
)

@app.callback(Output('querydata', 'children'),
              [Input('submit', 'n_clicks')],
              [State('stock', 'value'),
               State('obs', 'value'),
               State('lookback', 'value')]
              )

def get_data(n_clicks,stock, obs, lookback):
    if n_clicks != 0:
        data = md.QuandlStockData(apikey, stock, days=lookback)
        gen = mc.NormalDistribution(data.currentexmean, data.currentexvol)
        sim = mc.NaiveMonteCarlo(gen, obs=obs)
        dist = sim.simulated_distribution * data.market_data['adj_close'].iloc[-1]
        hist_dist = (data.market_data['percentchange'] * data.market_data['adj_close'].iloc[-1]).dropna()
        return (json.dumps({
            'data': data.market_data.to_json(date_format='iso', orient='records'),
            'dist': list(dist),
            'hist_dist': list(hist_dist),
            'currentvol': data.currentexvol,
            'currentexvol': data.currentexvol * np.sqrt(252),
            'currentswvol': data.currentswvol * np.sqrt(252),
            'currentexr': (1 + data.currentexmean) ** (252 / lookback) - 1,
            'currentswr': (1 + data.currentswmean) ** (252 / lookback) - 1,
            'percentVaR': np.nanpercentile(sim.simulated_distribution, 2.5)})
        )


@app.callback(Output('equityline', 'figure'),
              [Input('querydata', 'children'),
               Input('stock', 'value')])
def chart(data, stock):
    tempdata = json.loads(data)
    tempdata = pd.DataFrame(json.loads(tempdata['data']))
    line = go.Scatter(
        x=tempdata['date'],
        y=tempdata['adj_close'],
        name = stock + ' Adjusted Price'
    )

    line = go.Candlestick(x = tempdata['date'],
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
        title= stock + ' Adjusted Prices',
        xaxis=dict(
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
                )]
            )
        )
        )
    )
    fig = go.Figure(data=[line], layout=outlayout)
    return(fig)

@app.callback(Output('montecarlo', 'figure'),
              [Input('querydata', 'children')
               ])
def montecarlohistigram(simdata):
    simdata = json.loads(simdata)
    data = [
        go.Histogram(x=simdata['dist'],
                     histnorm='probability',
                     opacity=.75,
                     name='MC 1D Simulation')
    ]
    data.append(
        go.Histogram(x=simdata['hist_dist'],
                     histnorm='probability',
                     opacity=.75,
                     name='Historic 1D Distribution')
    )
    layout = go.Layout(barmode='overlay')
    fig = go.Figure(data=data, layout=layout)
    return(fig)


@app.callback(Output('metrics_table', 'children'),
              [Input('querydata', 'children')])
def summary_table(sim):
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
    names = ['Simulated Dollar 1D Value at Risk',
             'Simulated Percent 1D VaR',
             'Historic Dist 1D VaR',
             'Historic 1D Percent VaR @ 2 SD',
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
    return(html.Table(tbl_out, className='table'))
