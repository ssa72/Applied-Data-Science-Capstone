""" 
spacex_launch_records_dashboard.py

Plotly Dash Application for users to perform interactive visual analytics on SpaceX launch data in 
real time

Note: Only works on Python 3.8 due to certain dependencies.

When running in Python 3.8, install the required libraries with the following commands:

Install pandas dash:
>> python3.8 -m pip install pandas dash

Download the dataset:
>> wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

Download the skeleton Dash app:
>> wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_3/spacex_dash_app.py"


"""


# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create dash application
app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # Dropdown list to enable Launch Site selection
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"},
                {"label": "CCAFS LC-40", "value": "CCAFS LC-40"},
                {"label": "VAFB SLC-4E", "value": "VAFB SLC-4E"},
                {"label": "KSC LC-39A", "value": "KSC LC-39A"},
                {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"},
            ],
            value="ALL",
            placeholder="place holder here",
            searchable=True,
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={0: "0", 10000: "10000"},
            tooltip={"placement": "bottom", "always_visible": True},
            value=[min_payload, max_payload],
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    """
    Callback function for `site-dropdown` as input, `success-pie-chart` as output Function
    decorator to specify function input and output

    Args:
        entered_site (str): launch site from drop-down menu

    Returns:
        plotly figure: pie chart with data specified in drop-down menu

    """
    filtered_df = spacex_df
    if entered_site == "ALL":
        fig = px.pie(
            filtered_df,
            values="class",
            names="Launch Site",
            title="Success Count for all launch sites",
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        filtered_df = (
            filtered_df.groupby(["Launch Site", "class"])
            .size()
            .reset_index(name="count of class")
        )
        fig = px.pie(
            filtered_df,
            values="count of class",
            names="class",
            title=f"Total Success Launches for site {entered_site}",
        )
        return fig


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, slider):
    """
    Callback function and decorator for `site-dropdown` and `payload-slider` as inputs,
    'success-payload-scatter-chart` as output

    Args:
        entered_site (str): Launch site from drop-down menu
        slider (list): slider values

    Returns:
        plotly figure: scatter plot with data specified in range slider

    """
    filtered_df = spacex_df[
        (slider[0] <= spacex_df["Payload Mass (kg)"])
        & (spacex_df["Payload Mass (kg)"] <= slider[1])
    ]
    if entered_site == "ALL":
        return px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Launch Success Rate For All Sites",
        )
    # return the outcomes in pie chart for a selected site
    filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
    filtered_df["outcome"] = filtered_df[filtered_df["class"] == "Success"]
    return px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Launch Success Rate For " + entered_site,
    )


# Run the app
if __name__ == "__main__":
    app.run_server()
