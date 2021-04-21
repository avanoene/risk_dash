from base64 import urlsafe_b64encode
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_defer_js_import as dji

import dash_table as dt

from app import app, server
from pages import single_ticker, portfolio_metrics


with open('./README.md', 'r') as f:
    readme = f.read()

with open('./documentation/gettingstarted.md', 'r') as f:
    docs = f.read()


app.layout = dbc.Container(
    [
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    'Risk Dash Documentation',
                    href='/docs',
                ),
            ),
            dbc.NavItem(
                dbc.NavLink(
                    'Portfolio Dashboard',
                    href='/portfolio',
                ),
            ),
            dbc.NavItem(
                dbc.NavLink(
                    'Individual Security Dashboard',
                    href='/single',
                ),
            ),
        ],
        brand='Risk Dash',
        brand_href='/',
        color='light',
        id='nav'
    ),
    dbc.Container(id='page_content',fluid=True),
    html.Div(dt.DataTable(data=[{}]), style={'display' : 'none'}),
    dji.Import(src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/latest.js?config=TeX-AMS-MML_SVG")
    ],
    fluid=True
)

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


if __name__ == '__main__':
    print('Running')
    app.run_server()