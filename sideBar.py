import dash_bootstrap_components as dbc
from dash import html


def make_sidebar():
    # styling the sidebar
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
        "color": "grey",
        "overflow": "auto"
    }
    return html.Div(
        [
            html.Img(
                src="https://upload.wikimedia.org/wikipedia/commons/6/6a/Durga_eyes.svg",
                style={"width": "100%"}),
            html.Hr(),
            html.P("FHGR CDS-202 - Eyetracking Datensatz"),
            dbc.Nav(
                [
                    dbc.NavLink("Startseite", href="/", active="exact"),
                    dbc.NavLink("Datensatz", href="/data", active="exact"),
                    dbc.NavLink("Average Maps", href="/map", active="exact"),
                    dbc.NavLink("Average User", href="/user", active="exact"),
                    dbc.NavLink("User paths per map", href="/path", active="exact")
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )
