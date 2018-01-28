import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.offline import offline
import pandas as pd
import quandl
from pandas.tseries.offsets import BDay
from dateutil.relativedelta import relativedelta
import montecarlo as mc
import json
import numpy as np
import scipy.stats as stats

app = dash.Dash()

quandl.ApiConfig.api_key = 'ypi4REFshCpdRxC3PKyR'


time_options =['5D',
'10D',
'20D',
'3M',
'6M',
'1Y',
'5Y',
'10Y'
]

app.layout = html.Div([
    html.Link(rel='stylesheet',
              href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
              integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
              crossOrigin='anonymous'),
    html.Link(rel='stylesheet',
              href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css',
              integrity='sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp',
              crossOrigin='anoymous'),
    html.Script(src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
                integrity='sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa',
                crossOrigin='anoymous'),
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
        dcc.Input(
        id='lookback',
        type='number',
        placeholder='Lookback Period',
        value=80
        )],
        className='row'
    ),
    html.Div([
        html.Div(
            dcc.Graph(id='montecarlo'),
            className='col-md-6'
        ),
        html.Div(
            html.Div(
                id='metrics_table',
                className='col-md-6'
            )
        )
        ],
        className='row'
    )
    ],
    className='container-fluid'
)

@app.callback(Output('querydata', 'children'),
              [Input('submit', 'n_clicks')],
              [State('stock', 'value')]
              )

def get_data(n_clicks,stock):
    if n_clicks != 0:
        metadata = quandl.Dataset('WIKI/' + stock)
        date = metadata['newest_available_date']
        data = quandl.get_table('WIKI/PRICES',
                                ticker=stock,
                                date={'gte':(date - relativedelta(years=5))})
        return(data.to_json(date_format = 'iso', orient='records'))



@app.callback(Output('simdata', 'children'),
              [Input('querydata', 'children'),
               Input('obs', 'value'),
               Input('lookback', 'value')]
              )
def simulation(data, obs, lookback):
    tempdata = json.loads(data)
    tempdata = pd.DataFrame(tempdata)
    sim = mc.MonteCarlo(tempdata, lookback, exp=True)
    sim.gen.normaldist(obs)
    simobs = sim.gen.obs
    dist = simobs * tempdata['adj_close'].iloc[-1]
    hist_dist = (sim.market_data['percentchange'] * tempdata['adj_close'].iloc[-1]).dropna()
    return(json.dumps({'dist': list(dist),
                       'hist_dist':list(hist_dist),
                       'currentexvol': sim.currentexvol.values[0] * np.sqrt(252),
                       'currentswvol':sim.currentswvol.values[0] * np.sqrt(252),
                       'currentexr': (1 + sim.currentexmean.values[0]) ** (252/lookback) - 1,
                       'currentswr': (1 + sim.currentswmean.values[0]) ** (252/lookback) - 1,
                       'percentVaR': np.nanpercentile(simobs, 2.5)}))

@app.callback(Output('equityline', 'figure'),
              [Input('querydata', 'children'),
               Input('stock', 'value')])
def chart(data, stock):
    tempdata = json.loads(data)
    tempdata = pd.DataFrame(tempdata)
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
        title='Adjusted Prices',
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
              [Input('simdata', 'children')
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
              [Input('simdata', 'children')])
def summary_table(sim):
    simdata = json.loads(sim)
    var = np.nanpercentile(simdata['dist'], 2.5)
    percentvar = simdata['percentVaR']
    actvar = np.nanpercentile(simdata['hist_dist'], 2.5)
    simvol = np.nanstd(simdata['dist'])
    exvol = simdata['currentexvol']
    swvol = simdata['currentswvol']
    exreturn = simdata['currentswr']
    ewexreturn = simdata['currentexr']
    metrics = [var, percentvar, actvar, simvol, exvol, swvol, exreturn, ewexreturn]
    names = ['Simulated Dollar 1D Value at Risk',
             'Simulated Percent 1D VaR',
             'Historic Dist 1D VaR',
             'Simulated Volatility',
             'Historic Exponentially Weighted Vol',
             'Historic Simply Weighted Vol',
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
    tbl_out = tbl_out + [html.Tr([html.Td(i), html.Td(j)]) for i , j in zip(names, metrics)]
    return(tbl_out)


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':
    print('Running')
    app.run_server()