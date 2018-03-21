import json

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from app import app

import base64
import io

from objects import market_data as md, securities as sec
import pandas as pd
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
    csv_string = 'Type,Ticker,Ordered Price,Quantity\n'
    csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)
    return(csv_string)

def parse_content(contents, filename, date):
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

    return([html.Div([
        html.H5('File Contents'),
        html.H5(filename),
        html.H6(datetime.fromtimestamp(date).strftime('%m/%d/%Y %H:%M:%S')),
        dt.DataTable(rows = df.to_dict('records'))
    ], className = 'col-md-12'
    )]
    )

layout = html.Div(
    [
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
        ),
        html.Div(
            children=html.H5('Upload Portfolio'),
            id='uploadoutput',
            className = 'row'
        )
    ],
    className='container-fluid'
)

@app.callback(Output('uploadoutput', 'children'),
              [Input('input-data', 'contents'),
               Input('input-data', 'filename'),
               Input('input-data', 'last_modified')])
def output_upload(contents, filename, modified):
    if contents is not None:
        return(parse_content(contents, filename, modified))

