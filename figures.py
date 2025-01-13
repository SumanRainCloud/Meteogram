
Conversation opened. 1 read message.

Skip to content
Using Gmail with screen readers
4 of 34
Live weather
Inbox
Suman Halder <suman.halder@volocopter.com>
	
Wed, 31 Jul 2024, 11:48
	
to me

"""Standard components for figure layouts."""

 

from typing import Optional

from dash import dcc, dash_table

import dash_bootstrap_components as dbc

import numpy as np

import pandas as pd

import plotly.graph_objects as go

from pandas.errors import DataError

from datetime import datetime, timedelta

from app.config import VOLOCOLOR

import plotly.express as px

from dash import html

import pytz

 

# ruff: noqa: F401

from app.components import plotly_templates

 

 

def blank_fig(

    custom_annotation: Optional[str] = "No data available.",

    custom_figure_title: Optional[str] = None,

) -> go.Figure:

    """Generate empty figure to initialize dcc.Graph component.

 

    Args:

        custom_annotation: Optional(str): Graph annotation to display for blank figure.

        custom_figure_title: Optional(str): Graph title to display

                                            when showing blank figure.

 

    Returns:

        go.Figure: Empty figure.

    """

 

    fig = go.Figure(go.Scatter(x=[], y=[]))

    fig.update_layout(template=None, title=custom_figure_title)

    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)

    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    fig.add_annotation(

        x=0.5,

        y=1,

        xref="paper",

        yref="paper",

        text=custom_annotation,

        font=dict(family="Gotham", size=30, color=VOLOCOLOR),

        showarrow=False,

    )

 

    return fig

 

 

def generate_two_card_graph_layout(left_graph_id: str, right_graph_id: str) -> dbc.Card:

    """Generate layout component with two graphs in one card.

 

    Args:

        left_graph_id (str): Dash id of left graph.

        right_graph_id (str): Dash id of right graph.

 

    Returns:

        dbc.Card: Dash component.

    """

    return dbc.CardGroup(

        [

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        dcc.Graph(

                            id=left_graph_id,

                            figure=blank_fig(),

                            className="h-100",

                        ),

                    ),

                    style={"width": "auto"},

                ),

            ),

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        dcc.Graph(

                            id=right_graph_id,

                            figure=blank_fig(),

                            className="h-100",

                        ),

                    ),

                    style={"width": "auto"},

                ),

            ),

        ],

        className="gap-4 pt-4 graph-zoomed",

        style={"min-height": "500px"},

    )

 

 

def generate_two_card_graph_table_layout(

    right_graph_id: str,

    new_id,

) -> dbc.Card:

    """Generate layout component with two graphs in one card.

    Args:

        right_graph_id (str): Dash id of right graph.

 

    Returns:

        dbc.Card: Dash component.

    """

    return dbc.CardGroup(

        [

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.Div(

                                dash_table.DataTable(

                                    id=new_id,

                                    cell_selectable=False,

                                    style_as_list_view=True,

                                    style_table={"border": "none"},

                                    style_header={

                                        "font-weight": "700",

                                        "text-transform": "capitalize",

                                        "text-align": "center",

                                        "padding-inline-start": "0.5rem",

                                        "padding-inline-end": "0.5rem",

                                        "padding-top": "1rem",

                                        "padding-bottom": "1rem",

                                        "line-height": "2",

                                        "font-size": "0.75rem",

                                        "color": "#334363",

                                        "border-bottom-width": "none",

                                        "border-bottom-style": "none",

                                        "border-color": "#e5e7eb",

                                        "white-space": "nowrap",

                                        "background-color": "none!important",

                                    },

                                    style_data={

                                        "font-weight": "600",

                                        "text-align": "center",

                                        "padding-inline-start": "0.5rem",

                                        "padding-inline-end": "0.5rem",

                                        "padding-top": "0.5rem",

                                        "padding-bottom": "0.5rem",

                                        "font-size": "0.90rem",

                                        "line-height": "1.6",

                                        "height": "2rem",

                                        "border-bottom-width": "none",

                                        "border-bottom-style": "none",

                                    },

                                ),

                                style={"margin": "5px", "min-height": "50px"},

                            ),

                        ],

                        style={"padding": 0, "position": "relative"},

                    ),

                ),

                style={"width": "auto"},

            ),

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        dcc.Graph(

                            id=right_graph_id,

                            figure=blank_fig(),

                            className="h-100",

                        ),

                    ),

                ),

                style={"width": "auto"},

            ),

        ],

        className="gap-4 pt-4",

        style={"min-height": "500px"},

    )

 

 

def generate_linegraph(

    df: pd.DataFrame,

    columns: list,

    title: str,

    yaxes_title: str,

    exclude_zero_from_yrange: Optional[bool] = False,

    set_legend_top_left: bool = False,

    set_legend_top_right: bool = False,

    additional_plot=False,

    interval=None,

) -> go.Figure:

    """Helper function to generate a line graph figure for general purposes.

 

    Args:

        df (pd.DataFrame): Dataframe with data to display.

        columns (list): List of column names to plot traces for.

        title (str): Graph title.

        yaxes_title (str): Y axis title.

            Note: Title until first space character will be used for hover label,

                e.g. "Temperature (°C)" --> "Temperature"

        exclude_zero_from_yrange (Optional[bool], optional):

            Reset yaxis zoom of figure to focus on min/max without 0 values.

            Defaults to False.

        set_legend_top_left (bool): Set legend position to top left inside of graph.

        set_legend_top_right(bool): Set legend position to top right inside of graph.

 

    Returns:

        go.Figure: Plotly figure.

    """

 

    time_chosen = 1

    if interval == "10 Seconds":

        time_chosen = 10

    elif interval == "30 Seconds":

        time_chosen = 30

    elif interval == "2 Minutes":

        time_chosen = 120

    elif interval == "5 Minutes":

        time_chosen = 300

    # prepare subframe

    df_plot = df.loc[:, ["timestamp_utc", *columns]].copy()

 

    if df_plot.empty:

        return blank_fig()

 

    # build figure

    value_name = yaxes_title.split(" ")[0]

    fig = go.Figure()

    for col in columns:

        # for each trace use only part of the frame that is not NaN,

        # so we do not get breaks in the graphs at NaN

        df_trace = df_plot.loc[~df_plot[col].isna(), ["timestamp_utc", col]]

        fig.add_trace(

            go.Scatter(

                x=df_trace["timestamp_utc"].head(300),

                y=df_trace[col].head(300),

                name="Current",

                meta=value_name,

                hovertemplate="<i>Time</i>: %{x}<br><i>%{meta}</i>: %{y}<extra></extra>",

            )

        )

        if additional_plot is True:

            try:

                df_trace.set_index("timestamp_utc", inplace=True)

                shifting = time_chosen - 1

                df_trace["Rolling"] = (

                    df_trace.rolling(window=time_chosen).mean().shift(-shifting)

                )

                fig.add_trace(

                    go.Scatter(

                        x=df_trace.index[:300],

                        y=df_trace["Rolling"],

                        name=f" {interval} (running mean)",

                        meta=value_name,

                        # required for template structure

                        # ruff : noqa: E501

                        hovertemplate="<i>Time</i>: %{x}<br><i>%{meta}</i>: %{y}<extra></extra>",

                    )

                )

            except DataError:

                pass

 

    # layout and axes

    column_name_y_axis = columns[0]

    fig.update_layout(

        title=title,

        template="volo_linegraph",

        margin={"r": 0, "t": 30, "l": 0, "b": 0},

        showlegend=True,

        hovermode="closest",

        uirevision="0",

    )

    if set_legend_top_left:

        fig.update_layout(

            legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.01, orientation="v"),

        )

    if set_legend_top_right:

        fig.update_layout(

            legend=dict(

                yanchor="top", y=1.15, xanchor="right", x=1.00, orientation="v"

            ),

        )

    min_trace = df_trace[column_name_y_axis].min()

    ymin = max(0, min(0, min_trace - 5))

    fig.update_yaxes(

        range=[ymin, df_trace[column_name_y_axis].max() + 5],

        title_text=yaxes_title,

        hoverformat=".1f",

    )

    fig.update_xaxes(title_text="Time [Z]")

 

    # np.nanmax sometimes triggers "All-NaN slice encountered" runtime warning

    if exclude_zero_from_yrange:

        yaxis_range = [

            np.floor(

                np.nanmin(

                    df.loc[:, columns].replace(0, np.nan).values,

                    axis=None,

                )

            ),

            np.ceil(np.nanmax(df.loc[:, columns].values, axis=None)),

        ]

        fig.update_yaxes(

            range=yaxis_range,

            autorange=False,

        )

 

    return fig

 

 

def generate_48hours_linegraph(

    df: pd.DataFrame,

    columns: list,

    title: str,

    yaxes_title: str,

    set_legend_top_left: bool = False,

    set_legend_top_right: bool = False,

) -> go.Figure:

    """Helper function to generate a line graph figure for general purposes.

 

    Args:

        df (pd.DataFrame): Dataframe with data to display.

        columns (list): List of column names to plot traces for.

        title (str): Graph title.

        yaxes_title (str): Y axis title.

            Note: Title until first space character will be used for hover label,

                e.g. "Temperature (°C)" --> "Temperature"

        exclude_zero_from_yrange (Optional[bool], optional):

            Reset yaxis zoom of figure to focus on min/max without 0 values.

            Defaults to False.

        set_legend_top_left (bool): Set legend position to top left inside of graph.

        set_legend_top_right(bool): Set legend position to top right inside of graph.

 

    Returns:

        go.Figure: Plotly figure.

    """

    df_plot = df.loc[:, ["timestamp_utc", *columns]].copy()

 

    if df_plot.empty:

        return blank_fig()

 

    today = datetime.now()

    yesterday = today - timedelta(days=1)

    day_before_yesterday = today - timedelta(days=2)

 

    # Add a new column to indicate the day

    df["day"] = np.select(

        [

            df["timestamp_utc"].dt.date == today.date(),

            df["timestamp_utc"].dt.date == yesterday.date(),

            df["timestamp_utc"].dt.date == day_before_yesterday.date(),

        ],

        ["today", "yesterday", "day_before_yesterday"],

        default="other",

    )

 

    fig = go.Figure()

 

    df["time"] = df["timestamp_utc"].dt.time

 

    # Convert time to fractional hours for y-axis representation

    df["hour_fraction"] = df["timestamp_utc"].apply(

        lambda t: t.hour + t.minute / 60 + t.second / 3600

    )

 

    for col in columns:

        for day in ["today", "yesterday"]:

            df_plot = df[df["day"] == day]

 

            fig.add_trace(

                go.Scatter(

                    x=df_plot["hour_fraction"],

                    y=df_plot[col],

                    mode="lines",

                    name=f"{day.capitalize()}",

                    line=dict(

                        color=(

                            "rgba(255, 0, 0, 0.7)"

                            if day == "yesterday"

                            else (

                                "rgba(0, 0, 255, 0.7)"

                                if day == "today"

                                else "rgba(0, 255, 0, 0.7)"

                            )

                        )

                    ),

                    meta=yaxes_title,

                    # required for template structure

                    # pylint: disable-next=line-too-long

                    hovertemplate="<i>Time</i>: %{x}<br><i>%{meta}</i>: %{y}<extra></extra>",

                )

            )

    fig.update_layout(

        title=title,

        template="volo_linegraph",

        margin={"r": 0, "t": 30, "l": 0, "b": 0},

        showlegend=True,

        hovermode="closest",

        uirevision="0",

    )

    if set_legend_top_left:

        fig.update_layout(

            legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.01, orientation="v"),

        )

    if set_legend_top_right:

        fig.update_layout(

            legend=dict(

                yanchor="top", y=1.15, xanchor="right", x=1.00, orientation="v"

            ),

        )

    min_trace = df[columns[0]].min()

    if title == "Temperature":

        ymin = min_trace - 5

    else:

        ymin = max(0, min(0, min_trace - 5))

    fig.update_yaxes(

        range=[ymin, df[columns[0]].max() + 5],

        title_text=yaxes_title,

        hoverformat=".1f",

    )

    fig.update_xaxes(title_text="Time [UHR]")

 

    return fig

 

 

def generate_direction_average(dir: np.array) -> float:

    """

    Helper function to Calculate wind direction average.

 

    Args:

    Dir(np.average) -- list of angles to be averaged.

 

    Returns:

        value: Average for wind direction

 

    """

    ph = dir / 180 * np.pi

    ds = np.sin(ph)

    dc = np.cos(ph)

 

    wd0 = 180 / np.pi * np.arctan2(ds.mean(), dc.mean())

    if wd0 < 0:

        wd0 += 360

    mean_wd = wd0

    return mean_wd

 

 

def generate_polar_chart(

    df: pd.DataFrame,

    fig_title: str,

) -> go.Figure:

    """Helper function to generate a Bar Polar Chart from most recend record.

 

    Args:

        df (pd.DataFrame): Dataset to be used for Graph creation.

        column (str): Column to use for Graph creation.

        title (str): Title of Graph.

 

    Returns:

        go.Figure: Bar Polar Figure

    """

    bins_mag = [0, 2, 4, 6, 8, 10, 12, 100]

    bins_mag_labels = [

        "0.0-2.0",

        "2.0-4.0",

        "4.0-6.0",

        "6.0-8.0",

        "8.0-10.0",

        "10.0-12.0",

        ">12",

    ]

 

    bins_dir = [

        0,

        11.25,

        33.75,

        56.25,

        78.75,

        101.25,

        123.75,

        146.25,

        168.75,

        191.25,

        213.75,

        236.25,

        258.75,

        281.25,

        303.75,

        326.25,

        348.75,

        360.00,

    ]

    bins_dir_labels = [

        "N",

        "NNE",

        "NE",

        "ENE",

        "E",

        "ESE",

        "SE",

        "SSE",

        "S",

        "SSW",

        "SW",

        "WSW",

        "W",

        "WNW",

        "NW",

        "NNW",

        "North",

    ]

 

    df["mag_binned"] = pd.cut(df["wind_average_kt"], bins_mag, labels=bins_mag_labels)

    df["dir_binned"] = pd.cut(

        df["wind_direction_average_deg"], bins_dir, labels=bins_dir_labels

    )

    dfe = df[

        ["mag_binned", "dir_binned", "timestamp_utc"]

    ].copy()  # here i am creating a new dataframe, with necessary columns

    # only (except the last one, which I will convert to frequencies column

    dfe.rename(

        columns={"timestamp_utc": "freq"}, inplace=True

    )  # changing the last column to represent frequencies

    g = dfe.groupby(["mag_binned", "dir_binned"]).count()  # grouping

    g.reset_index(inplace=True)

    g["percentage"] = g["freq"] / g["freq"].sum()

    g["percentage%"] = g["percentage"] * 100

    g["Magnitude [kn]"] = g["mag_binned"]

    g = g.replace(r"North", "N", regex=True)  # replacing remaining Norths with N

 

    fig = px.bar_polar(

        g,

        r="percentage%",

        theta="dir_binned",

        color="Magnitude [kn]",

        color_discrete_sequence=px.colors.sequential.Plasma_r,

        title=fig_title,

    )

    fig.update_layout(dragmode=False)

    return fig

 

 

def generate_all_calculation(df: pd.DataFrame, timerange_choice) -> pd.DataFrame:

    """Helper function to generate wind parameter calculations.

 

    Args:

        df (pd.DataFrame): Dataset to be used for calculation.

    Returns:

        Ave_tab: dataframe with calculated values

    """

    # Live values

    ws_live = df["wind_average_kt"][0]

    wd_live = df["wind_direction_average_deg"][0]

    wg_live = df["wind_gust_kt"][0]

    wgd_live = df["wind_gust_direction_deg"][0]

    temperature_live = df["air_temperature_deg_c"][0]

    humidity_live = df["humidity_percent"][0]

    pressure_live = df["air_pressure_hpa"][0]

    density_live = round(df["density"][0], 2)

    qnh_live = round(df["qnh"][0], 2)

    da_live = round(df["da"][0], 2)

    # Average Wind speed for last 2 Minutes

    ws_choice = df["wind_average_kt"].head(timerange_choice).mean().round(1)

    # Max Wind Gust for the last 60 Seconds

    wg_choice = df["wind_gust_kt"].head(timerange_choice).max()

    # Average Wind direction for last 2 Minutes

    wd_choice = generate_direction_average(

        np.array(df["wind_direction_average_deg"].head(timerange_choice))

    ).round()

    # The direction of the max wind gust for the last 120 Seconds

    wgd_choice = df[df["wind_gust_kt"] == wg_choice].iloc[0, 4]

    # temperature average last 2 minutes

    temperature_choice = (

        df["air_temperature_deg_c"].head(timerange_choice).mean().round(1)

    )

    # humidity average last 2 minutes

    humidity_choice = df["humidity_percent"].head(timerange_choice).mean().round(1)

    # pressure average last 2 minutes

    pressure_choice = df["air_pressure_hpa"].head(timerange_choice).mean().round(1)

    density_choice = round(df["density"].head(timerange_choice).mean(), 2)

    qnh_choice = round(df["qnh"].head(timerange_choice).mean(), 2)

    da_choice = round(df["da"].head(timerange_choice).mean(), 2)

    # Average Wind speed for last 10 Minutes

    ws_600 = df["wind_average_kt"].head(600).mean().round(1)

    # Average Wind direction for last 2 Minutes

    wd_600 = generate_direction_average(

        np.array(df["wind_direction_average_deg"].head(600))

    ).round()

    # Max Wind Gust for the last 10 Minutes

    wg_600 = df["wind_gust_kt"].head(600).max()

    # The direction of the max wind gust for the last 10 minutes

    wgd_600 = df[df["wind_gust_kt"] == wg_600].iloc[0, 4]

    # temperature average last 10 mins minutes

    temperature_600 = df["air_temperature_deg_c"].head(600).mean().round(1)

    # humidity average last 10 minutes

    humidity_600 = df["humidity_percent"].head(600).mean().round(1)

    # pressure average last 10 minutes

    pressure_600 = df["air_pressure_hpa"].head(600).mean().round(1)

    density_600 = round(df["density"].head(600).mean(), 2)

    qnh_600 = round(df["qnh"].head(600).mean(), 2)

    da_600 = round(df["da"].head(600).mean(), 2)

    data = [

        ("Wind Speed [kts]", ws_live, ws_choice, ws_600),

        ("Wind Dir [deg]", wd_live, wd_choice, wd_600),

        ("Gust Speed [kts]", wg_live, wg_choice, wg_600),

        ("Gust Direction [deg]", wgd_live, wgd_choice, wgd_600),

        (

            "Temperature [° C]",

            temperature_live,

            temperature_choice,

            temperature_600,

        ),

        ("Humidity [%]", humidity_live, humidity_choice, humidity_600),

        ("Pressure [hPa]", pressure_live, pressure_choice, pressure_600),

        ("Density [kg/m3]", density_live, density_choice, density_600),

        ("Density Altitude [ft]", da_live, da_choice, da_600),

        ("QNH ", qnh_live, qnh_choice, qnh_600),

    ]

    time_mapping = {

        1: "Current",

        10: "10 Seconds",

        30: "30 Seconds",

        120: "2 Minutes",

        300: "5 Minutes",

    }

    time_chosen = time_mapping.get(timerange_choice)

    ave_tab = pd.DataFrame(

        data, columns=["Parameter", "Current", time_chosen, "10 mins"]

    )

 

    return ave_tab

 

 

def generate_wind_direction(theta, theta2, r, runway, figure_title, interval):

    """Helper function to generate a wind direction plot from most recend record.

 

    Args:

        theta (int): Wind direction data to be used for Graph creation.

        r (float): radial distance from the center of the plot.

        title (str): Title of Graph.

 

    Returns:

        go.Figure: Bar Polar Figure

    """

    df = pd.DataFrame({"theta": [theta], "r": [r], "theta2": [theta2]})

    # Create the polar scatter plot with default marker symbols

    fig = px.scatter_polar(df, r="r", theta="theta", title=figure_title).update_layout(

        polar_radialaxis_showticklabels=False,

        polar_radialaxis_range=[0, 1.85],

        polar_radialaxis_showgrid=False,

        polar_radialaxis_showline=False,

        polar_angularaxis_showgrid=False,

        polar_angularaxis=dict(dtick=30),

        xaxis_visible=False,

        xaxis_showticklabels=False,

        yaxis_visible=False,

        yaxis_showticklabels=False,

    )

    runway_number = runway.split("-")

 

    # Define the angles for the black line and text labels

    line_theta = [int(runway_number[0]) * 10, int(runway_number[1]) * 10]

    # Add the black line trace

    line_trace = go.Scatterpolar(

        r=[r, r],

        theta=line_theta,

        mode="lines+text",

        line=dict(color="black", width=30),

        opacity=0.9,

        showlegend=False,

    )

    fig.add_trace(line_trace)

 

    # Add the white dashed line trace on top of the black line

    dashed_trace = go.Scatterpolar(

        r=[r * 0.8, r * 0.8],

        theta=line_theta,

        mode="lines",

        line=dict(color="white", width=3, dash="longdash"),

        showlegend=False,

    )

    fig.add_trace(dashed_trace)

 

    # add the text traces on both sides of the black line

    fig.add_trace(

        go.Scatterpolar(

            r=[r * 0.85],

            theta=[line_theta[0]],

            mode="text",

            text=str(int(line_theta[1] / 10)),

            textfont=dict(size=12, color="white"),

            hoverinfo="none",

            textposition="top center",

            showlegend=False,

        )

    )

 

    fig.add_trace(

        go.Scatterpolar(

            r=[r * 0.95],

            theta=[line_theta[1]],

            mode="text",

            text=str(int(line_theta[0] / 10)),

            textfont=dict(size=12, color="white"),

            hoverinfo="none",

            textposition="top center",

            showlegend=False,

        )

    )

 

    big_tick_angles = np.linspace(0, 360, num=12, endpoint=False)

 

    # Add tick traces to the polar plot

    for angle in big_tick_angles:

        fig.add_trace(

            go.Scatterpolar(

                r=[r * 1.2],

                theta=[angle],

                mode="lines+markers",

                line=dict(color="black", width=2),

                marker=dict(

                    symbol="line-ew-open", size=16, color="black", angle=angle - 90

                ),

                hoverinfo="skip",

                opacity=1.0,

                textfont=dict(color="black", size=10),

                textposition="bottom center",

                showlegend=False,

            )

        )

 

    small_tick_angles = np.linspace(0, 360, num=36, endpoint=False)

 

    for angle in small_tick_angles:

        if angle in big_tick_angles:

            continue

        fig.add_trace(

            go.Scatterpolar(

                r=[r * 1.22],

                theta=[angle],

                mode="lines+markers",

                line=dict(color="black", width=2),

                marker=dict(

                    symbol="line-ew-open", size=8, color="black", angle=angle - 90

                ),

                hoverinfo="skip",

                opacity=1.0,

                textfont=dict(color="black", size=10),

                textposition="bottom center",

                showlegend=False,

            )

        )

 

    # Add the marker symbol of arrow

    fig.add_trace(

        go.Scatterpolar(

            r=[r * 1.3],

            theta=[theta],

            mode="markers",

            name=interval,

            showlegend=True,

            marker=dict(

                symbol="triangle-down",

                opacity=1,

                size=28,

                line=dict(width=2, color="black"),

                color="red",

                angle=theta,

            ),

        ),

        row=1,

        col=1,

    )

    fig.add_trace(

        go.Scatterpolar(

            r=[r * 1.3],

            theta=[theta2],

            mode="markers",

            name="Current",

            showlegend=True,

            marker=dict(

                symbol="triangle-down",

                opacity=1,

                size=28,

                line=dict(width=2, color="black"),

                color="blue",

                angle=theta2,

            ),

        ),

        row=1,

        col=1,

    )

    fig.update_layout(dragmode=False)

    return fig

 

 

def calculate_flight_parameters(

    track, wind_speed, wind_direction_degrees, target_airspeed, beta

):

    # Conversion factors

    deg2rad = np.pi / 180

    track_degrees = track

    # Convert angles to radians

    track = track_degrees * deg2rad

    wind_direction = wind_direction_degrees * deg2rad

 

    # Calculations for solving quadratic equation

    a = 1

    b = (

        2

        * wind_speed

        * (

            np.cos(wind_direction) * np.cos(track)

            + np.sin(wind_direction) * np.sin(track)

        )

    )

    c = wind_speed**2 - target_airspeed**2

 

    roots = np.roots([a, b, c])  # root of the equation

    gs = roots.max()  # groundspeed

    # target air speed direction

    tasd = (

        np.arctan2(

            (gs * np.sin(track) + wind_speed * np.sin(wind_direction)),

            (gs * np.cos(track) + wind_speed * np.cos(wind_direction)),

        )

        / deg2rad

    )

 

    # Ensuring TAS is positive and between 0 and 360 degrees

    tasd = (tasd + 360) % 360 if tasd < 0 else tasd

 

    hdg = tasd - beta

 

    # Ensure heading is between 0 and 360 degrees

    hdg = (hdg + 360) % 360 if hdg < 0 else hdg

 

    return {

        "TAS": tasd,

        "beta": beta,

        "Groundspeed [kts]": gs,

        "Heading [°]": hdg,

        "Windspd [kt]": wind_speed,

        "Winddir [°]": wind_direction_degrees,

    }

 

 

def wind_part(location):

    """The layout for the wind calculation for individuaal pages

 

    Args:

        location (string): The weather station identifier

 

    Returns:

        wind_part (table): Table for the wind calculation

    """

 

    wind = html.Table(

        [

            html.Tr(

                [

                    html.Td(),

                    html.Td(),

                    html.Td(),

                    html.Td(),

                    html.Td(),

                    html.Label("Track-"),

                    dcc.Input(

                        id=f"runway_direction1_{location}",

                        type="number",

                        value=115,

                        min=0,

                        max=359,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(),

                    html.Td(),

                    html.Label("Track-"),

                    dcc.Input(

                        id=f"runway_direction2_{location}",

                        type="number",

                        value=295,

                        min=1,

                        max=360,

                        style={"width": "100px"},

                    ),

                ],

                className="volo-table-th",

            ),

            html.Tr(

                [

                    html.Td(html.Label("TAS")),

                    html.Td(),

                    html.Td(html.Label("BETA")),

                    html.Td(),

                    html.Td(html.Label("Groundspeed [kts]")),

                    html.Td(),

                    html.Td(

                        html.Label("Heading [°]"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(html.Label("Groundspeed [kts]")),

                    html.Td(),

                    html.Td(html.Label("Heading [°]")),

                    html.Td(),

                ],

                className="volo-table-th",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_1_{location}",

                        type="number",

                        value=5,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_1_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_1_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_1_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(html.Div(id=f"wind_calc_2_groundspeed_{location}")),

                    html.Td(),

                    html.Td(html.Div(id=f"wind_calc_2_heading_{location}")),

                ],

                className="volo-table",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_2_{location}",

                        type="number",

                        value=7,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_2_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_3_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_3_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_4_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_4_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_3_{location}",

                        type="number",

                        value=10,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_3_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(html.Div(id=f"wind_calc_5_groundspeed_{location}")),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_5_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(html.Div(id=f"wind_calc_6_groundspeed_{location}")),

                    html.Td(),

                    html.Td(html.Div(id=f"wind_calc_6_heading_{location}")),

                ],

                className="volo-table",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_4_{location}",

                        type="number",

                        value=13,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_4_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_7_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_7_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_8_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_8_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_5_{location}",

                        type="number",

                        value=15,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_5_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_9_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_9_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_10_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_10_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

                className="volo-table",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_6_{location}",

                        type="number",

                        value=17,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_6_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_11_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_11_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_12_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_12_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_7_{location}",

                        type="number",

                        value=20,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_7_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_13_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_13_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_14_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_14_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

                className="volo-table",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_8_{location}",

                        type="number",

                        value=23,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_8_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_15_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_15_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_16_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_16_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_9_{location}",

                        type="number",

                        value=25,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_9_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_17_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_17_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_18_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_18_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

                className="volo-table",

            ),

            html.Tr(

                [

                    dcc.Input(

                        id=f"tas_10_{location}",

                        type="number",

                        value=27,

                        min=1,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    dcc.Input(

                        id=f"beta_10_{location}",

                        type="number",

                        value=0,

                        style={"width": "100px"},

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_19_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_19_heading_{location}"),

                        className="volo-table-td",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_20_groundspeed_{location}"),

                        className="volo-table-normal",

                    ),

                    html.Td(),

                    html.Td(

                        html.Div(id=f"wind_calc_20_heading_{location}"),

                        className="volo-table-normal",

                    ),

                ],

            ),

        ],

        className="gap-4 pt-4 bordered-table",

        style={

            "border": "2px solid black",

            "min-height": "500px",

            "padding-top": "1rem",

        },

    )

    return wind

 

 

def map_on_street(latitude, longitude, location, center_lat, center_lon):

    """

    Creates a scattermapbox figure showing weather station locations on a street map.

 

    Args:

        latitude (list): A list of latitude values for each weather station.

        longitude (list): A list of longitude values for each weather station.

        location (list): A list of location names for each weather station.

        center_lat (float): The latitude value for the center of the map.

        center_lon (float): The longitude value for the center of the map.

 

    Returns:
...

[Message clipped]  View entire message
	
runway parvezislam14@gmail.com
