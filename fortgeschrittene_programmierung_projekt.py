import plotly.express as px
import pandas as pd
from PIL import Image
import os
from dash import Dash, dcc, html, Input, Output
from dash import dash_table as dt
from sideBar import make_sidebar
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

PATH = "data/all_fixation_data_cleaned_up.csv"

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Dashboard Eyetracking - Fortgeschrittene Programmierung"
data = pd.read_csv(PATH, encoding="cp1252", delimiter="\t")

# the lambda function sorts users to be like: u1, u2 instead of u1, u10
users = sorted(data["user"].unique(), key=lambda string: float(string[1:]))
# get all map names
maps = sorted(data["StimuliName"].unique())

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "color": "grey"
}

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    make_sidebar(),
    content
])


def make_scatter_by_user_map(df: pd.DataFrame, user_name: str, map_name: str):
    # remove all unnecessary users and maps
    filtered_data = df[df["StimuliName"] == map_name]
    filtered_data = filtered_data[filtered_data["user"] == user_name]

    image_path = f"data/stimuli/{map_name}"
    # checking if image exists and if data for that image exists
    if os.path.exists(image_path) and len(filtered_data) > 0:
        im = Image.open(image_path)
        fig = px.imshow(im)
        filtered_durations = [i/10 for i in filtered_data["FixationDuration"].tolist()]
        fig.add_trace(go.Scatter(
            x=filtered_data["MappedFixationPointX"],
            y=filtered_data["MappedFixationPointY"],
            mode='lines+markers',
            name="test",
            marker=dict(size=filtered_durations,
                        colorscale='Viridis'),
        ))
        return fig
    return px.imshow(Image.open("data/error.png"))


@app.callback(
    Output(component_id="user_map_path", component_property="figure"),
    [Input(component_id='user-dropdown', component_property='value'),
     Input(component_id='maps-dropdown', component_property='value')]
)
def user_map_paths(user_name, map_name):
    return make_scatter_by_user_map(data, user_name, map_name)


# average map
@app.callback(
    Output(component_id="user_average", component_property="figure"),
    Input(component_id='user-dropdown', component_property='value')
)
def user_average(user_name):
    # remove all unnecessary users
    filtered_data = data[data["user"] == user_name]

    # seperate color and gray
    colored = filtered_data[filtered_data["description"] == "color"]
    grayed = filtered_data[filtered_data["description"] == "gray"]

    # prepare dataframes to plot
    prepared_colored = colored.groupby("StimuliName")["FixationDuration"].mean().tolist()
    prepared_gray = grayed.groupby("StimuliName")["FixationDuration"].mean().tolist()

    labels = list(set(filtered_data[filtered_data["description"] == "color"]["StimuliName"].tolist()))
    prepared_labels = [i[3:len(i) - 7] for i in labels]
    return {
        'data': [
            {'x': prepared_labels, 'y': prepared_colored, 'type': 'bar', 'name': 'Farbig'},
            {'x': prepared_labels, 'y': prepared_gray, 'type': 'bar', 'name': 'Graustufen'},
        ],
        'layout': {
            'title': f"Average looking time (ms) per user on {user_name}"
        }
    }


# average map
@app.callback(
    Output(component_id="maps_average", component_property="figure"),
    Input(component_id='maps-dropdown', component_property='value')
)
def maps_average(map_name):
    # remove all unnecessary maps
    filtered_data = data[data["StimuliName"] == map_name]
    # group users
    user_time = filtered_data.groupby("user")["FixationDuration"].mean().tolist()
    labels = filtered_data["user"].unique()
    return {
        'data': [
            {'x': labels, 'y': user_time, 'type': 'bar', 'name': 'Average Looking Time per user'},
        ],
        'layout': {
            'title': f"Average looking time per user on {map_name}"
        }
    }


# make sites
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page_content(pathname):
    if pathname == "/":
        return [
            html.H1('Startseite - Fortgeschrittene Programmierung', style={'textAlign': 'center'}),
            html.Br(),
            html.H2("Willkommen zum Dashboard von Alex, Ajshe, Drin, Louis und Stephane!"),
            html.H3("Dieses Dashboard wurde im Jahr 2022 im Modul Fortgeschrittene Programmiertechniken erstellt."),
            html.H4("Wir befinden uns im 1. Frühlingssemster des Bachelor Studiengang Computational und Data Science. "
                    "(2. Semester)"),
            html.P(
                "Der Datensatz wurde uns von den Dozenten vorgegeben. Es handelt sich um Eyetrackingdaten einer echten Studie.")
        ]
    elif pathname == "/data":
        return [
            html.H1('Datensatz', style={'textAlign': 'center'}),
            # Table can be searched
            dt.DataTable(
                id='tbl', data=data.to_dict('records'),
                columns=[{"name": i, "id": i} for i in data.columns],
                filter_action='native',
            ),
        ]
    elif pathname == "/map":
        maps_options = [{"label": i, "value": i} for i in maps]
        return [
            html.H1('Karte wählen', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='maps-dropdown',
                options=maps_options,
                value=maps_options[0]["value"]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="maps_average",
                    )
                ]
            ),
        ]
    elif pathname == "/user":
        user_options = [{"label": i, "value": i} for i in users]
        return [
            html.H1('User wählen', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='user-dropdown',
                options=user_options,
                value=user_options[0]["value"]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="user_average",
                    )
                ]
            ),
        ]
    elif pathname == "/path":
        user_options = [{"label": i, "value": i} for i in users]
        map_options = [{"label": i, "value": i} for i in maps]
        return [
            html.H1('User und Karte wählen', style={'textAlign': 'center'}),
            html.H5("User:"),
            dcc.Dropdown(
                id='user-dropdown',
                options=user_options,
                value=user_options[0]["value"]
            ),
            html.H5("Karte:"),
            dcc.Dropdown(
                id='maps-dropdown',
                options=map_options,
                value=map_options[0]["value"]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="user_map_path",
                    )
                ]
            ),
        ]
    return [
        html.Div(
            dbc.Container(
                [
                    html.H1("404: not found", className="display-3"),
                    html.Hr(className="my-2"),
                    html.P(f"The pathname {pathname} was not recognised...",
                           className="lead",
                           ),
                ],
                fluid=True,
                className="py-3",
            ),
            className="p-3 bg-light rounded-3",
        )
    ]


server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
