import dash
import dash_bootstrap_components as dbc

style_sheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=style_sheets,)

server = app.server
app.config.suppress_callback_exceptions = True

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
                tex2jax: {
                inlineMath: [['$','$']],
                displayMath: [['$$', '$$']],
                processEscapes: true
                }
            });
            </script>
            {%renderer%}
        </footer>
    </body>
</html>
"""