import json

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from app import app

import base64
import io
import pandas as pd
import plotly.graph_objs as go
import numpy as np

from objects import market_data as md, securities as sec
from apiconfig import quandl_apikey as apikey
from datetime import datetime

import urllib

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

def create_template():
    csv_string = 'Type,Ticker,Ordered Date,Ordered Price,Quantity\n'
    csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)
    return(csv_string)

def parse_content(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8'))
            )
        elif 'xls' in filename:
            df = pd.read_excel(
                io.BytesIO(decoded)
            )
    except Exception as e:
        print(e)
        return([html.Div(['There was an error processing this file'])])

    if 'Ordered Date' in df.columns:
        df['Ordered Date'] = pd.to_datetime(df['Ordered Date'])
    return(df)

layout = html.Div(
    [
        html.Div(
            [html.Div([
                html.H2('Upload Portfolio Data'),
                html.A(
                    'Download Template',
                    id='template',
                    download='template.csv',
                    href = create_template(),
                    target='_blank'
                ),
                dcc.Upload(
                    id='input-data',
                    children=html.Div([
                        'Drag or Drop Template or ',
                        html.A('Select Template')
                    ],
                    ),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                )
            ],
            className='col-md-12'
            )],
            className='row'
        ),
        html.Div(
            html.Div(
                dt.DataTable(
                    rows=[{}],
                    id='portfolio',
                    columns=['Type','Ticker', 'Ordered Date', 'Ordered Price', 'Quantity']
                ),
                className='col-md-12'
            ),
            className = 'row'
        ),
        html.Div(
            [html.Div(
                html.Table(
                    id='mtm',
                    className = 'table'
                ),
                className='col-md-6'
            ),
            html.Div(
                dcc.Graph(
                    id='portfolio_weights'
                ),
                className ='col-md-6'
            )],
            className='row'
        )
    ]
)

@app.callback(Output('portfolio', 'rows'),
              [Input('input-data', 'contents'),
               Input('input-data', 'filename')])
def output_upload(contents, filename):
    if contents is not None:
        df = parse_content(contents, filename)
        rows = df.to_dict('records')
        return(rows)

@app.callback(Output('table', 'children'),
              [Input('portfolio', 'rows')])
def displayport(contents):
    if contents is not None and contents != [{}]:
        df = pd.DataFrame.from_dict(contents)
        #port = create_portoflio(df)
        header = df.columns.tolist()
        tbl = [html.Tr([html.Th(i) for i in header])]
        tbl = tbl + [html.Tr([html.Td(j) for j in df.loc[i]]) for i in df.index]
        return(tbl)

@app.callback(Output('portfolio_weights', 'figure'),
              [Input('portfolio', 'rows')])
def create_pie(contents):
    if contents is not None and contents != [{}]:
        df = pd.DataFrame.from_dict(contents)
        df['portval'] = [a * b
                         for a,b
                         in zip([float(i) for i in df['Quantity'].values],
                                [float(i) for i in df['Ordered Price'].values])
                        ]
        totalval = df['portval'].sum()
        shorts = df[df['portval'] < 0].sort_values('portval')
        longs = df[df['portval'] >= 0].sort_values('portval', ascending=False)
        tickers = [i for i in longs['Ticker']]
        tickers += [i for i in shorts['Ticker']]
        tickers += ['Total']
        # base
        base = [0]
        base += [i for i in longs['portval']]
        base += [i for i in shorts['portval']][1:]
        base = np.cumsum(base).tolist()
        base += [0]

        trace0 = go.Bar(
            x = tickers,
            y = base,
            marker=dict(
                color='rgba(1,1,1,0)'
            )
        )
        #long positions
        trace1 = go.Bar(
            x = tickers,
            y = [i for i in longs['portval']] + [0 for i in shorts['portval']] + [0],
            marker = dict(color='rgba(63, 127, 191, 0.9)')
        )
        #short positions
        trace2 = go.Bar(
            x=tickers,
            y=[0 for i in longs['portval']] + [i for i in shorts['portval']] + [0],
            marker=dict(color='rgba(178, 76, 76, 0.9)')
        )
        #total
        trace3 = go.Bar(
            x = tickers,
            y = [0 for i in longs['portval']] + [0 for i in shorts['portval']] + [totalval],
            marker = dict(color='rgba(76, 178, 76, 0.9)')
        )
        data = [trace0, trace1, trace2, trace3]
        layout = go.Layout(barmode='stack')
        return(go.Figure(data=data, layout=layout))