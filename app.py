import pandas as pd
from dash import html, dcc, dash
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import math

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# read data
df = pd.read_csv('cohorts.csv')
df.drop(columns='Unnamed: 0', inplace=True)

# list of countries
countries = list(df.Country.unique())
countries.sort()
countries.insert(0, 'All')


def cohorts_table(df=df, country='All'):
    if country != 'All':
        df = df[df['Country'] == country]

    # Group the data by columns CohortMonth','CohortIndex' then aggreate by column 'CustomerID'
    cohort_data = df.groupby(
        ['CohortMonth', 'CohortIndex'])['CustomerID'].apply(pd.Series.nunique).reset_index()

    # Take the cohort_data and plumb it into a Pivot Table. Setting index, columns and values as below.
    cohort_count = cohort_data.pivot_table(index='CohortMonth',
                                           columns='CohortIndex',
                                           values='CustomerID')

    # select all the rows : select the first column
    cohort_size = cohort_count.iloc[:, 0]
    # Divide the cohort by the first column
    retention = cohort_count.divide(cohort_size, axis=0)
    retention.round(3)  # round the retention to 3 places

    z = retention.values.tolist()
    def to_text(x): return '' if math.isnan(x) else '{:0.0f}%'.format(x*100)
    z_text = [list(map(to_text, row)) for row in z]
    y = ['Dec10', 'Jan11', 'Feb11', 'Mar11', 'Apr11', 'May11', 'Jun11', 'Jul11',
         'Aug11', 'Sep11', 'Oct11', 'Nov11', 'Dec11']

    fig = ff.create_annotated_heatmap(
        z=z,
        x=list(range(len(retention.columns))),
        y=y[:len(z)],
        annotation_text=z_text,
        colorscale='Viridis')

    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    return fig


# initialize App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Cohort Analysis: Understand you produc's lifetime"

app.layout = html.Div(
    children=[
        html.Div(children=[
            html.H1(children='E-commerce Cohort Analysis',
                    className='header-title')  # ,
            # html.P(children='', className='header-description')
        ],
            className='header'),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Select country',
                                className='menu-title'),
                        dcc.Dropdown(
                            id='country-filter',
                            options=[{'label': i, 'value': i} for i in countries],
                            value='All',
                            clearable=False,
                            searchable=True,
                            className='dropdown',
                        )
                    ]
                )
            ],
            className='menu'
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(id='heatmap', figure=cohorts_table()),
                    className='card'
                )
            ],
            className='wrapper'
        )
    ],
)


@app.callback(
    Output('heatmap', 'figure'),
    [Input('country-filter', 'value')])
def update_figure(selected_country):
    return cohorts_table(country=selected_country)


if __name__ == "__main__":
    app.run_server(debug=True)
