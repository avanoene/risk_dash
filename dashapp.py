import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app
from pages import single_ticker, portfolio_metrics

with open('./README.md', 'r') as f:
    readme = f.read()

app.css.append_css(
    {'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
     'integrity' : 'sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
     'crossOrigin' : 'anonymous'}
)

app.layout = html.Div(
    [html.Link(rel='stylesheet',
          href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
          integrity='sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
          crossOrigin='anonymous'),
    html.Link(rel='stylesheet',
          href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css',
          integrity='sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp',
          crossOrigin='anonymous'),
    html.Script(src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
            integrity='sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa',
            crossOrigin='anonymous'),
    dcc.Location(id='url', refresh=False),
    html.Nav(
        [
            html.A(
                'Risk Dash',
                href='/'
            ),
            html.Div(
                [
                    html.A(
                        'Portfolio',
                        href='/portfolio',
                        className='nav-item nav-link'
                    ),
                    html.A(
                        'Individual Security',
                        href='/single',
                        className='nav-item nav-link'
                    )
                ],
                className='navbar-collapse'
            )

        ],
        className='nav navbar-toggleable-md navbar-inverse'
    ),
    html.Div(id='page_content', className = 'container'),
    html.Div(dt.DataTable(rows=[{}]), style={'display' : 'none'})
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
        else:
            return(dcc.Markdown(readme))


if __name__ == '__main__':
    print('Running')
    app.run_server()