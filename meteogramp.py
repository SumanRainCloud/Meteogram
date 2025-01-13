"""This is it- making meteograms"""
"""All generic figure generating functions defined here"""

import dash_bootstrap_components as dbc
from PIL import Image
from dash import html, dcc
from datetime import datetime
import base64
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
import io
from app.data.data import symbols_list
from plotly.figure_factory import create_quiver
import math
import pytz
from timezonefinder import TimezoneFinder

matplotlib.use("Agg")


def create_local_meteogram(df, path):
"""Helper function to generate a line graph figure for general purposes.

Args:
df (pd.DataFrame): Dataframe with data to display.
path (str): path for symbol reading.
Returns:
go.Figure: Plotly figure.
"""
fig = go.Figure()
fig = px.line(
df,
x="Hour",
y="TEMPERATURE_GROUND_LEVEL",
line_shape="linear",
labels={"TEMPERATURE_GROUND_LEVEL": "Temperature (°C)"},
)
fig.update_traces(line_color="#0000ff", line_width=5)
fig.add_trace(
go.Bar(
x=df["Hour"],
y=df["RELATIVE_HUMIDITY"],
name="Rel. Hum",
opacity=0.5,
marker_color="green",
yaxis="y2",
)
)

images = []
symbol_list = symbols_list()
symbols = {}
for symbol in symbol_list:
symbols[symbol] = df[df["symbol_show"] == symbol]["Hour"].tolist()
for symbol, positions in symbols.items():
for position in positions:
if fig.layout.width is not None:
sizex = 0.3 * fig.layout.width
else:
sizex = 1.6

if fig.layout.height is not None:
sizey = 0.3 * fig.layout.height
else:
sizey = 1.6
image_dict = {
"source": Image.open(f"{path}/{symbol}.png"),
"x": position,
"y": 1,
"xref": "x",
"yref": "y",
"sizex": sizex,
"sizey": sizey,
"xanchor": "center",
"yanchor": "bottom",
"layer": "above",
}
images.append(image_dict)
annotations = []

shapes = [
{
"type": "rect",
"x0": 0, # Add Sunrise
"y0": 0,
"x1": 0, # Add Sunset
"y1": df["TEMPERATURE_GROUND_LEVEL"].max() + 10,
"fillcolor": "yellow",
"opacity": 0.3,
"layer": "below",
"line": {"width": 0},
}
]

tickvals_secondary = np.arange(0.5, 24, 1)
fig.update_xaxes(
tickmode="array",
tickvals=df["Hour"],
ticktext=df["Time"],
tickangle=45,
)
fig.update_layout(
title_text="Meteogram",
xaxis={"title": "Time (hours)", "dtick": 1, "showgrid": True},
xaxis2={
"title": "Time",
"side": "top",
"overlaying": "x",
"dtick": 1,
"showgrid": True,
"tickvals": tickvals_secondary,
},
yaxis={
"title": "Temperature (°C)",
"title_font": {"color": "#0000ff"},
"tickfont": {"color": "#0000ff"},
},
yaxis2={
"title": "Relative Humidity",
"overlaying": "y",
"side": "right",
"title_font": {"color": "green"},
"tickfont": {"color": "green"},
},
showlegend=False,
images=images,
shapes=shapes,
annotations=annotations,
)
return fig


def read_image(filename, path):
"""Helper function to read images for general purposes.

Args:
filename (str): filename
path (str): path name
Returns:
image: encoded image.
"""
with open(f"{path}/{filename}", "rb") as f:
image_data = f.read()
return "data:image/png;base64," + base64.b64encode(image_data).decode()


def draw_wind_arrow(wind_direction_degrees):
"""Helper function to generate a wind direction arrow for general purposes.

Args:
wind_direction_degrees (int): Plot detail regarding wind arrow direction.
Returns:
go.Figure: Plotly figure.
"""
wind_direction_radians = np.radians(-wind_direction_degrees + 90)

fig, ax = plt.subplots(figsize=(4, 4))

arrow_length = 0.3
arrow_head_width = 0.15
arrow_head_length = 0.2

arrow_dx = arrow_length * np.cos(wind_direction_radians)
arrow_dy = arrow_length * np.sin(wind_direction_radians)

arrowhead_x = -arrow_dx
arrowhead_y = -arrow_dy

ax.arrow(
arrow_dx,
arrow_dy,
arrowhead_x,
arrowhead_y,
head_width=arrow_head_width,
head_length=arrow_head_length,
fc="blue",
ec="blue",
)

max_val = max(abs(arrow_dx), abs(arrow_dy))
ax.set_xlim(-max_val, max_val)
ax.set_ylim(-max_val, max_val)
ax.set_aspect("equal", adjustable="datalim")

ax.axis("off")

buffer = io.BytesIO()
plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0, dpi=300)
plt.close(fig)
buffer.seek(0)

image_data = buffer.getvalue()
encoded_image = base64.b64encode(image_data).decode()
return f"data:image/png;base64,{encoded_image}"


def get_current_hour(lat, lon):
"""Helper function to get current hour for general purposes.

Args:
lat (float): latitude
lon (float): longitude
Returns:
str: current hour.
"""
tf = TimezoneFinder()
timezone_str = tf.timezone_at(lng=lon, lat=lat)
tz = pytz.timezone(timezone_str)
utc_now = datetime.now(pytz.utc)
local_now = utc_now.astimezone(tz)
return local_now.hour


def table_today(df_local, path):
"""Helper function to generate a line graph figure for general purposes.

Args:
df_local (pd.DataFrame): Dataframe with data to display.
path (str): path to symbols
Returns:
html.Table: Table returned.
"""

table_rows = []
if df_local is None or len(df_local) == 0:
return html.Table(
table_rows,
className="table-sam",
style={"width": "100%", "font-family": "Gotham"},
)

param_names = {
"symbol_show": "Weather Condition",
"TEMPERATURE_GROUND_LEVEL": "Temperature",
"DEW_POINT_TEMPERATURE_GROUND_LEVEL": "Dew point",
"WIND_DIRECTION_10M": "Wind Direction",
"WIND_SPEED_10M": "Wind Speed",
"RELATIVE_HUMIDITY": "Relative Humidity",
"PROBABILITY_OF_PRECIPITATION": "Precipitation probability",
}

current_hour = get_current_hour(
df_local["LATITUDE"].iloc[0], df_local["LONGITUDE"].iloc[0]
)

param_row = [html.Th("")]
# pylint: disable=W0612
for i, data_row in df_local.iterrows():
time = data_row["Hour"]
is_current_hour = time == current_hour
cell_style = {"background-color": "#e1ffe1" if is_current_hour else ""}
param_row.extend([html.Th(data_row["Time"], style=cell_style)])
table_rows.append(html.Tr(param_row))
# pylint: enable=W0612
# pylint: disable=C0206
# pylint: disable=C0201
for param in param_names.keys():
table_row = [html.Th(param_names[param])]
for i, data_row in df_local.iterrows():
if param == "symbol_show":
cell_content = html.Img(
src=read_image(data_row[param] + ".png", path),
style={"width": "50px"},
)
elif param == "WIND_DIRECTION_10M":
cell_content = html.Img(
src=draw_wind_arrow(data_row["WIND_DIRECTION_10M"]),
style={"width": "50px"},
)
else:
cell_content = data_row[param]

is_current_hour = data_row["Hour"] == current_hour
cell_style = {"background-color": "#e1ffe1"} if is_current_hour else {}
table_row.extend([html.Td(cell_content, style=cell_style)])

table_rows.append(html.Tr(table_row))
# pylint: enable=C0206
# pylint: enable=C0201
table_layout = html.Table(
table_rows,
className="table-sam",
style={"width": "100%", "font-family": "Gotham"},
)
return table_layout


def generate_one_card_layout(df, path) -> dbc.Card:
"""Generate layout component with one graphs in one card.

Args:
df (pd.DataFrame): Data passed for generation of figure
plot (str): tab name passed.
path (str): symbol location.

Returns:
dbc.Card: Dash component.
"""
card_style = {
"max-height": "400px",
"overflow-y": "auto",
}
if df is None or len(df) == 0:
empty_table = html.Table(
[], className="table-sam", style={"width": "100%", "font-family": "Gotham"}
)
return dbc.Card(
dbc.CardBody([empty_table]),
style=card_style,
)
card_content = table_today(df, path)
return dbc.Card(
dbc.CardBody([card_content]),
style=card_style,
)


def generate_one_card_layout_for_figure(graph_id):
"""Generate layout component with one graphs in one card.

Args:
graph_id (str): Dash id of left graph.

Returns:
dbc.Card: Dash component.
"""
return dbc.CardGroup(
[
dbc.Card(
dbc.CardBody(
dcc.Graph(
id=graph_id,
figure=blank_fig(),
className="h-100",
),
),
),
],
className="gap-4 pt-4",
style={"min-height": "500px"},
)


def blank_fig(
custom_annotation: Optional[str] = "Load Data",
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
font={"family": "Gotham", "size": 30},
showarrow=False,
)
return fig


def create_bar_chart_with_marker(df_filtered):
"""
Creates a bar chart using Plotly Express for the provided DataFrame,
adds a marker for wind gusts greater than 17, and positions the legend
in the lower left corner.

Args:
- df (pandas.DataFrame): DataFrame containing the required data.

Returns:
- fig (plotly.graph_objs.Figure): Plotly Figure object with the bar
chart and marker.
"""

fig = px.bar(
df_filtered,
x="Time",
y="WIND_SPEED_10M",
hover_data=["WIND_GUST_10M", "Date"],
color="WIND_GUST_10M",
color_continuous_scale="tealgrn",
labels={"WIND_SPEED_10M": "Wind Speed (kn)", "Time": "Time"},
)

gust_greater_than_17 = df_filtered[df_filtered["WIND_GUST_10M"] > 17]

if not gust_greater_than_17.empty:
fig.add_trace(
go.Scatter(
x=gust_greater_than_17["Time"],
y=gust_greater_than_17["WIND_SPEED_10M"],
mode="markers",
marker={"symbol": "diamond", "color": "red", "size": 10},
name="Wind Gust > 17",
showlegend=True,
)
)
fig.update_xaxes(
tickangle=45,
)
fig.update_layout(
legend={
"x": 0,
"y": 1,
"traceorder": "normal",
"bgcolor": "rgba(255, 255, 255, 0.5)",
"bordercolor": "rgba(0, 0, 0, 0.5)",
"borderwidth": 1,
}
)
fig.update_layout(title="Wind Forecast")
return fig


def create_precipitation_area_plot(df):
"""
Creates an area plot using Plotly Express for the provided DataFrame
filtered by a specific date. Modifies the hover data to display
'Precipitation Type' and customizes the figure's title, x-axis, and
y-axis labels.

Args:
- filtered_df (pandas.DataFrame): DataFrame containing the required data.

Returns:
- fig (plotly.graph_objs._figure.Figure): Plotly Figure object.
"""

# Mapping precipitation types
precipitation_map = {
0: "Unknown",
1: "Rain",
2: "Rain and snow",
3: "Snow",
4: "Sleet",
5: "Freezing rain",
6: "Hail",
}
filtered_df = df.copy()
filtered_df["Precipitation Type"] = filtered_df["PRECIPITATION_TYPE"].map(
precipitation_map
)

fig = px.area(
filtered_df,
x="Time",
y="PROBABILITY_OF_PRECIPITATION",
hover_data={"Precipitation Type": True},
)
fig.update_xaxes(
tickangle=45,
)
fig.update_yaxes(range=[0, 100])
fig.update_layout(
title="Precipitation Probability ",
xaxis_title="Time",
yaxis_title="Probability of Precipitation",
)

return fig


def quiver_plot(df_filtered):
"""
Creates a quiver plot for the provided DataFrame
filtered by a specific date' and customizes the figure's title,
x-axis, and y-axis labels.

Args:
- filtered_df (pandas.DataFrame): DataFrame containing the required data.

Returns:
- fig (plotly.graph_objs._figure.Figure): Plotly Figure object.
"""
df = df_filtered.copy()
df["wind_dir_radians"] = np.radians(df["WIND_DIRECTION_10M"])

df["opposite_wind_dir_radians"] = df["wind_dir_radians"] - np.pi

df["U"] = np.sin(df["opposite_wind_dir_radians"]) * 2
df["V"] = np.cos(df["opposite_wind_dir_radians"]) * 2

fig = create_quiver(
df.index,
df["WIND_SPEED_10M"],
df["U"],
df["V"],
scale=0.5,
scaleratio=0.5,
angle=math.pi / 9,
name="Wind Velocity",
)
fig.update_xaxes(
tickmode="array",
tickvals=df.index,
ticktext=df["Time"],
tickangle=45,
)
fig.update_layout(
xaxis_title="Time",
yaxis_title="Wind Speed (kn)",
)

return fig


def METAR_generate_surface_wind(wind_direction_degrees, wind_speed_knots):
if wind_speed_knots == 0:
return "00000KT" # CALM condition

wind_direction_str = "{:03d}".format(int(wind_direction_degrees / 10) * 10)
wind_speed_str = "{:02d}".format(round(wind_speed_knots))
surface_wind = wind_direction_str + wind_speed_str + "KT"
return surface_wind


def METAR_generate_visibility(visibility_meters):
if visibility_meters < 50:
return "0000" # Less than 50 meters visibility
elif visibility_meters >= 10000:
return "9999" # 10km or more visibility
else:
return "{:04d}".format(int(visibility_meters))


def identify_weather(weather_code):
weather_conditions = {
"mist": [110, 10],
"drizzle": [
20,
24,
50,
51,
52,
53,
54,
55,
56,
57,
58,
59,
68,
69,
122,
125,
150,
151,
152,
153,
154,
155,
156,
157,
158,
167,
168,
],
"freezing": [
24,
56,
57,
66,
67,
125,
145,
146,
147,
148,
154,
155,
156,
164,
165,
166,
],
"ice_crystals": [178],
"rain": [
21,
23,
24,
25,
26,
27,
58,
59,
60,
61,
62,
63,
64,
65,
66,
67,
68,
69,
80,
81,
82,
83,
84,
87,
88,
89,
90,
91,
92,
93,
94,
95,
97,
123,
125,
140,
141,
143,
160,
161,
162,
163,
164,
165,
166,
167,
168,
181,
182,
183,
184,
192,
195,
],
"snow": [
20,
22,
23,
26,
36,
37,
38,
39,
68,
69,
70,
71,
72,
73,
74,
75,
76,
77,
78,
83,
84,
85,
86,
87,
88,
89,
90,
93,
94,
95,
97,
122,
124,
127,
128,
129,
167,
168,
170,
171,
172,
173,
177,
185,
186,
187,
192,
195,
],
"volcanic_ash": [4],
"fog": [
11,
12,
28,
40,
41,
42,
43,
44,
45,
46,
47,
48,
49,
76,
77,
78,
120,
130,
131,
132,
133,
134,
135,
],
"hail": [27, 89, 90, 93, 94, 95, 96, 97, 99, 189, 193, 196],
"dust": [6, 7, 8, 9, 30, 31, 32, 33, 34, 35, 98, 127, 128, 129, 104, 105, 111],
"squall": [18, 118],
"funnel_cloud": [19],
"small_hail": [87, 88],
"ice_pellets": [23, 79, 174, 175, 176],
"thunderstorm": [
17,
29,
95,
96,
97,
98,
99,
126,
190,
191,
192,
193,
194,
195,
196,
],
}
List_of_occurrences = []
for condition, codes in weather_conditions.items():
if weather_code in codes:
List_of_occurrences.append(condition)

return List_of_occurrences


def get_abbreviation(weather_condition):
abbreviation_mapping = {
"mist": "BR",
"drizzle": "DZ",
"freezing": "FZ",
"ice_crystals": "IC",
"rain": "RA",
"snow": "SN",
"volcanic_ash": "VA",
"fog": "FG",
"hail": "GR",
"dust": "DU",
"squall": "SQ",
"funnel_cloud": "FC",
"small_hail": "GS",
"ice_pellets": "PL",
"thunderstorm": "TS",
}

abbreviations = []
for condition in weather_condition:
abbreviation = abbreviation_mapping.get(condition, "")
if abbreviation:
abbreviations.append(abbreviation)

return "".join(abbreviations)


def get_prefix_and_weather_condition(weather_code):
prefix_mapping = {
"-": [
30,
31,
32,
36,
38,
50,
51,
56,
58,
60,
61,
66,
68,
70,
71,
85,
80,
83,
87,
89,
91,
93,
95,
96,
141,
143,
145,
147,
151,
154,
157,
161,
164,
167,
174,
171,
181,
185,
191,
192,
193,
],
"+": [
37,
39,
54,
55,
57,
59,
64,
65,
67,
69,
74,
75,
81,
84,
86,
88,
90,
92,
94,
97,
99,
142,
144,
146,
148,
153,
156,
158,
163,
166,
168,
173,
176,
183,
187,
194,
195,
196,
],
"MI": [11, 12],
"BL": [36, 38, 127, 128, 129],
"BC": [11, 41, 131],
"SH": [
25,
26,
27,
80,
81,
82,
83,
84,
86,
87,
88,
89,
90,
180,
181,
182,
183,
184,
185,
186,
187,
192,
195,
],
}
abbreviation_final = ""
weather_condition = identify_weather(weather_code)
abbrv = get_abbreviation(weather_condition)
prefixes = ""
for prefix, codes in prefix_mapping.items():
if weather_code in codes:
prefixes = prefixes + prefix
if not prefixes:
return abbrv
else:
abbreviation_final = prefixes + abbrv
return abbreviation_final


# Combined function


def generate_cloud(cloud_coverage, cloud_base_height, visibility_m):
if math.isnan(cloud_base_height):
cloud_base_height = 9999
cloud_base_height_feet = round(cloud_base_height * 3.28084, -2)
cloud_coverage_str = ""
cavok = ""
if cloud_coverage == 0:
cavok = generate_cavok(
visibility_m,
cloud_base_height_feet,
)
if cloud_coverage >= 1 and cloud_coverage <= 2:
cloud_coverage_str = "FEW"
elif cloud_coverage >= 3 and cloud_coverage <= 4:
cloud_coverage_str = "SCT"
elif cloud_coverage >= 5 and cloud_coverage <= 7:
cloud_coverage_str = "BKN"
elif cloud_coverage == 8:
cloud_coverage_str = "OVC"
cloud_base_str = "{:03d}".format(int(cloud_base_height_feet / 100))
return cloud_coverage_str + cloud_base_str + cavok


def generate_cavok(
visibility_meters,
cloud_base_height_feet,
):
if visibility_meters >= 10000 and cloud_base_height_feet >= 5000:
return "CAVOK"
else:
return "NSC"


def report_temperature_and_dewpoint(temperature, dewpoint):
return f"{temperature:02d}/{dewpoint:02d}"


def report_QNH(QNH):
return f"Q{int(QNH)}"


def generate_observation_time():
utc_time = datetime.utcnow()

day_of_month = "{:02d}".format(utc_time.day)
time_of_observation = "{:02d}{:02d}".format(utc_time.hour, utc_time.minute)

# Generate the observation time string
observation_time = day_of_month + time_of_observation + "Z"

return observation_time


def encode_metar(df_local):
if df_local is None:
return "METAR NOT GENERATED (NO DATA AVAILABLE)"
else:
current_hour = get_current_hour(
df_local["LATITUDE"].iloc[0], df_local["LONGITUDE"].iloc[0]
)
df = df_local[df_local["Hour"] == current_hour]
observation_time = generate_observation_time()
surface_wind = METAR_generate_surface_wind(
int(df["WIND_DIRECTION_10M"]), int(df["WIND_SPEED_10M"])
)
visibility = METAR_generate_visibility(int(df["VISIBILITY"]))
cloud = generate_cloud(
int(df["LOW_CLOUD_COVER"]),
int(df["CEILING_HEIGHT_AGL"]),
int(df["VISIBILITY"]),
)
weather = get_prefix_and_weather_condition(int(df["WEATHER_CODE"]))
temperature = report_temperature_and_dewpoint(
int(df["TEMPERATURE_GROUND_LEVEL"]),
int(df["DEW_POINT_TEMPERATURE_GROUND_LEVEL"]),
)
# qnh = report_QNH(pressure)
metar = (
"METAR"
+ " "
+ observation_time
+ " "
+ surface_wind
+ " "
+ visibility
+ " "
+ weather
+ " "
+ cloud
+ " "
+ temperature
)
return metar

