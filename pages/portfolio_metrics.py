import json

import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
from app import app

import base64
import io
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import pickle

from risk_dash import market_data as md, securities as sec
from apiconfig import quandl_apikey as apikey
from datetime import datetime

import urllib

def create_portoflio(input):
    temp = []
    for i in input.index:
        tempdata = md.QuandlStockData(apikey, input.loc[i, 'Ticker'], days=80)
        tempsecurity = sec.Equity(
            input.loc[i, 'Ticker'],
            market_data = tempdata,
            ordered_price = input.loc[i, 'Ordered Price'],
            quantity=input.loc[i, 'Quantity'],
            date_ordered=input.loc[i, 'Ordered Date'])
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
                    data=[{} for i in range(10)],
                    columns = ['Type','Ticker', 'Ordered Date', 'Ordered Price', 'Quantity'],
                    id='portfolio'
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

@app.callback(Output('portfolio', 'data'),
              [Input('input-data', 'contents'),
               Input('input-data', 'filename')])
def output_upload(contents, filename):
    if contents is not None:
        df = parse_content(contents, filename)
        data = df.to_dict('records')
        return(data)

@app.callback(Output('mtm', 'children'),
              [Input('portfolio', 'data')])
def displayport(contents):
    if contents is not None and contents != [{}]:
        df = pd.DataFrame.from_dict(contents)
        portfolio = create_portoflio(df)
        portfolio.mark()
        marked = portfolio.marked_portfolio
        df['Type'] = [i + ' Equity' for i in df['Ticker']]
        df.loc[:,'Current Price'] = df['Type'].map(
            {
                i : portfolio.port[i].market_data.current_price()
                for i in portfolio.port.keys()
            }
        )
        df.loc[:,'Initial Value'] = df['Type'].map(
            {i : j[0] for i, j in marked.items()}
        )
        df.loc[:,'Market Value'] = df['Type'].map(
            {i : j[1] for i, j in marked.items()}
        )
        df.loc[:,'Return %'] = ((df['Market Value'] - df['Initial Value']) / df['Initial Value'].abs()) * 100
        df = df[['Ticker', 'Current Price', 'Initial Value', 'Market Value', 'Return %']]
        header = df.columns.tolist()
        tbl = [html.Tr([html.Th(i) for i in header])]
        tbl = tbl + [html.Tr([html.Td(j) for j in df.loc[i]]) for i in df.index]
        tbl += [
            html.Tr(
                [
                html.Td('Total'),
                html.Td(''),
                html.Td(df['Initial Value'].sum()),
                html.Td(df['Market Value'].sum()),
                html.Td(((df['Market Value'].sum() - df['Initial Value'].sum()) / df['Initial Value'].sum()) * 100)
            ]
            )
        ]
        return(tbl)

@app.callback(Output('portfolio_weights', 'figure'),
              [Input('portfolio', 'data')])
def create_vis(contents):
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
        if [i for i in shorts['portval']] == []:
            base += [i for i in longs['portval']][:-1]
        else:
            base += [i for i in longs['portval']]
        base += [i for i in shorts['portval']][1:]
        base = np.cumsum(base).tolist()
        base += [0]

        trace0 = go.Bar(
            x = tickers,
            y = base,
            marker=dict(
                color='rgba(1,1,1,0)'
            ),
            showlegend=False
        )
        #long positions
        trace1 = go.Bar(
            x = tickers,
            y = [i for i in longs['portval']] + [0 for i in shorts['portval']] + [0],
            marker = dict(color='rgba(63, 127, 191, 0.9)'),
            showlegend = False
        )
        #short positions
        trace2 = go.Bar(
            x=tickers,
            y=[0 for i in longs['portval']] + [i for i in shorts['portval']] + [0],
            marker=dict(color='rgba(178, 76, 76, 0.9)'),
            showlegend=False
        )
        #total
        trace3 = go.Bar(
            x = tickers,
            y = [0 for i in longs['portval']] + [0 for i in shorts['portval']] + [totalval],
            marker = dict(color='rgba(76, 178, 76, 0.9)'),
            showlegend=False
        )
        data = [trace0, trace1, trace2, trace3]
        layout = go.Layout(barmode='stack')
        return(go.Figure(data=data, layout=layout))