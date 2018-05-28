from base64 import urlsafe_b64encode
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app, server
from pages import single_ticker, portfolio_metrics


with open('./README.md', 'r') as f:
    readme = f.read()

with open('./Documentation.md', 'r') as f:
    docs = f.read()

app.css.append_css(
    {'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
     'integrity' : 'sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
     'crossOrigin' : 'anonymous'}
)

app.css.append_css(
    {
    'external_url':'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css',
    'integrity':'sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp',
    'crossOrigin':'anonymous'
    }
)

app.scripts.append_script(
    {'external_url':"https://code.jquery.com/jquery-3.2.1.slim.min.js",
     'integrity':"sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN",
     'crossorigin':"anonymous"
     }
)

app.scripts.append_script(
    {'external_url':"https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js",
     'integrity' : "sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q",
     'crossorigin':"anonymous"
     }
)
app.scripts.append_script(
    {'external_url':"https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js",
     'integrity':"sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl",
     'crossorigin':"anonymous"
    }
)

app.layout = html.Div(
    [
    dcc.Location(id='url', refresh=False),
    html.Nav(
        [
            html.A(
                'Risk Dash',
                href='/',
                className='navbar-brand'
            ),
            html.Div(
                html.Ul(
                    [
                        html.Li(
                            html.A(
                                'Documentation',
                                href='/docs',
                                className='nav-link'
                            ),
                            className='nav-item'
                        ),
                        html.Li(
                            html.A(
                                'Portfolio',
                                href='/portfolio',
                                className='nav-link'
                            ),
                            className='nav-item'
                        ),
                        html.Li(
                            html.A(
                                'Individual Security',
                                href='/single',
                                className='nav-link'
                            ),
                            className='nav-item'
                        )
                    ],
                    className='nav navbar-nav'
                ),
                className='collapse navbar-collapse',
                id='navitems'
            )


        ],
        className='navbar navbar-expand-lg navbar-light',
        id='nav'
    ),
    html.Div(id='page_content', className = 'container'),
    html.Div(dt.DataTable(rows=[{}]), style={'display' : 'none'}),

]
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