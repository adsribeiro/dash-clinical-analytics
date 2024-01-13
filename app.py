from dash import Dash, dcc, html
import plotly.express as px
import polars as pl
import dash_ag_grid as dag  
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from datetime import datetime

FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)
# external_stylesheets = ["https://codepen.io/chriscoyier/pen/gHnGD.scss"]

template_theme1 = "darkly"
url_theme1 = dbc.themes.DARKLY



app = Dash(__name__,external_stylesheets=[url_theme1, dbc_css, FONT_AWESOME])


# ================ Styles =======================
tab_card = {
   'height': '100%',
   'width':'100%', 
   'auto-size':True
   }
main_config = {
   #  "hovermode": "x unified",
   #  "yaxis":{"showgrid":False},
   #  "xaxis":{"showgrid":False},
    "legend": {
        "yanchor":"top",
        "y": 0.9,
        "xanchor": "left",
        "x":0.1,
        "title":{"text": None},
        "font": {"color":"white"},
        "bgcolor": "rgba(0,0,0,0.0)"},
        "paper_bgcolor": "rgba(0, 0, 0, 0.0)",
        "plot_bgcolor": "rgba(0, 0, 0, 0.0)",
    "margin": {"l":10, "r":10, "t":10, "b":10} 
    }
layout = dict(
        margin=dict(l=70, b=50, t=50, r=50),
        modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        # annotations=annotations,
        # shapes=shapes,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
            color="white"
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" ", color="white"
        ),
        hovermode="closest",
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0.0)",
        paper_bgcolor="rgba(0, 0, 0, 0.0)",
        # legend=dict(font=dict(color="white")),
    )

layout_table =  dict(
              margin=dict(l=0, r=0, b=0, t=0, pad=0),
              xaxis=dict(
                  showgrid=False,
                  showline=False,
                  showticklabels=False,
                  zeroline=False,
              ),
              yaxis=dict(
                  showgrid=False,
                  showline=False,
                  showticklabels=False,
                  zeroline=False,
              ),
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
          )
trace = dict(
        mode="markers",
        marker=dict(size=14, line=dict(width=1, color="#ffffff")),
        fillcolor="#2c82ff",
        selected=dict(marker=dict(color="#ff6347", opacity=1)),
        unselected=dict(marker=dict(opacity=0.1)),
        # selectedpoints=selected_index,
        hoverinfo="text",
        # customdata=patient_id_list,
        # text=text_wait_time,
    )
config_graph = dict(displayModeBar = False, showTips=False)

# ============= Data Ingestion ==================
wkDayNames = {1 : "Monday", 2 : "Tuesday", 3 : "Wednesday", 4 : "Thursday", 5 : "Friday", 6 : "Saturday", 7 : "Sunday" }
df = (
    pl.scan_csv('./datasets/clinical_analytics.csv', try_parse_dates=True)
    .with_columns(
    pl.col(["Appt Start Time","Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p"),
    pl.col(["Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p").dt.weekday().alias("wk_day"),
    pl.col(["Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p").dt.weekday().alias("wk_day_name").replace(wkDayNames),
    pl.col(["Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p").dt.day().alias("day"),
    pl.col(["Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p").dt.hour().alias("hour"),
    pl.col(["Check-In Time"]).str.strptime(pl.Datetime, format="%Y-%m-%d %I:%M:%S %p").dt.strftime("%H %p").alias("hour_am_pm")
    )
)
# ================== Std Df with zeros ==================
# Weekday list
week_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
hours = [f"{str(i).zfill(2)} AM" if i < 12 else (f"{str(i).zfill(2)} PM" if i != 12 else "12 PM") for i in range(0, 24)]
dia_da_semana_numerico = {dia: idx + 1 for idx, dia in enumerate(week_day)}
# Dataframe with 0
data = {"wk_day_name": week_day, **{hour: [0] * len(week_day) for hour in hours}}
df_std = pl.DataFrame(data)
df_std = (
    df_std.melt(id_vars="wk_day_name",variable_name="hour_am_pm", value_name="Number of Records")
    .with_columns(
    pl.col("wk_day_name").replace(dia_da_semana_numerico).alias("wk_day").cast(pl.Int8)
    )
)
columns_order = ["wk_day","wk_day_name","hour_am_pm","Number of Records"]
df_std = df_std.select(columns_order)

options_clinic = [clinic for clinic in df.select(pl.col("Clinic Name").unique()).collect().to_series()]
options_admit_source = sorted([clinic for clinic in df.select(pl.col("Admit Source").fill_null("Information Unavailable").unique()).collect().to_series()])

# # =============== AG Grid - Table===============

columnDefs = [
    {
        "headerName": "Department",
        "field": "Department",
        # "type": "rightAligned",
        "wrapText": True,
        "pinned": "left",
        # "autoHeight": True, 
        "width": 130
    },
    {
        "headerName": "Wait Time Minutes",
        "field": "Wait Time Minutes",
        "cellRenderer": "DCC_GraphClickData",
        #  "type": "rightAligned",
        # "maxWidth": 900,
        # "minWidth": 400,
        "width": 450,
        "wrapText": True,
        # "autoHeight": True,
        # "flex":2
        "cellClass":['my-class1','my-class2', 'text-center']

    },
    {
        "headerName": "Care Score",
        "field": "Care Score",
        "cellRenderer": "DCC_GraphClickData",
        # "maxWidth": 900,
        # "minWidth": 400,
        "width": 320,
        "wrapText": True,
        "pinned": "right",
        # "autoHeight": True,
        # "flex":1
        "cellClass":['my-class1','my-class2', 'text-center']

    },
]
defaultColDef = {
    "resizable": False,
    "sortable": False,
    "wrapHeaderText": True,
    "autoHeaderHeight": True,
    "suppressMovable": True,
    # "marryChildren": True
    'flex': 1
}
table = dag.AgGrid(
    id="portfolio-table",
    className="ag-theme-alpine-dark", #"dbc",
    columnDefs=columnDefs,
    defaultColDef=defaultColDef,
    rowData=[],# subset.to_dicts(), #to_dict('records'),
    columnSize="sizeToFit",
    dashGridOptions={"rowHeight": 70,"embedFullWidthRows": True,
                     "alignedGrids": ["bottom-grid-footer"], "suppressHorizontalScroll": True,},
    
)
# =============== Layout =======================

app.layout = dbc.Container(
   id="app-container",
   children=[
   dbc.Row([
      # Col 1 - Filters
      dbc.Col([
         dbc.Card([
            dbc.CardBody([
               html.Legend("Clinic Analytics"),
               html.Hr(),
               html.H2("Welcome to the Clinical Analytics Dashboard"),
               html.Hr(),
               html.P("Explore clinic patient volume by time of day, waiting time, and care score. Click on the heatmap to visualize patient experience at different time points."),
               html.Header("Select Clinic",style={"margin-top":"10px","margin-bottom":"10px"}),
               dcc.Dropdown(
                  id="clinic-dropdown",
                  className="dbc",
                  options=options_clinic,
                  value=[],
                  multi=True,
                #   persistence=True,
                #   persistence_type='session'
               ),
               html.Hr(),
               html.Header("Select Check-In Time",style={"margin-top":"10px","margin-bottom":"10px"}),
               dcc.DatePickerRange(
                   id="datepicker",
                   className="dbc",
                   min_date_allowed=df.select(pl.col("Check-In Time").dt.strftime("%Y-%m-%d").min()).collect().item(),
                   max_date_allowed=df.select(pl.col("Check-In Time").dt.strftime("%Y-%m-%d").max()).collect().item(),
                #    display_format="DD MM YYYY",
                #    persistence=True
               ),
               html.Hr(),
               html.Header("Select Admit Source",style={"margin-top":"10px","margin-bottom":"10px"}),
                dcc.Dropdown(
                  id="admit-source-dropdown",
                  className="dbc",
                  options=options_admit_source,
                  value=[],
                #   placeholder="Select Admit Source",
                  multi=True,
                  style={"margin-top":"10px"},
                #   persistence=True,
                #   persistence_type='session'
               ),
                html.Hr(),
                 dbc.Button("Apply Filters",id="apply-filter", color="primary", className="me-1", disabled=False),
               
            ])
         ], style=tab_card)
      ], sm=12, md=4, lg=4),
      # Col 2 - Graphs
      dbc.Col([
          dbc.Row([
              dbc.Card([
                  dbc.CardBody([
                      html.Legend("Patient Volume"),
                      html.Hr(),
                      dcc.Loading([dcc.Graph(id="heatmap-graph", className="dbc")], className="dbc")
                  ])
              ], style=tab_card)
          ]),
          dbc.Row([
              dbc.Card([
                  html.Legend("Patient Wait Time and Satisfactory Scores"),
                  html.Hr(),
                  dbc.CardBody([
                     dcc.Loading([
                         table,
                        #  bottom_grid
                         ], className="dbc")
                      
                    #   dcc.Graph(id="other-graph", className="dbc")
                  ])
              ], style=tab_card)
          ], style={"margin-top":"10px"}),
      ], sm=12, md=8, lg=8),
   ], style={'height': '100vh'})
], fluid=True, style={'height': '100vh', 'padding':'20px'}, class_name="dbc")


# =============== Callbacks ====================
# Activate filter

@app.callback(
        Output("apply-filter", "disabled"),
        Input("clinic-dropdown","value"),
        Input("admit-source-dropdown", "value"),
        Input("datepicker","start_date"),
        Input("datepicker","end_date")
)
def activate_filter(clinic, admit_source, start_date, end_date):
    if not(clinic and admit_source and start_date and end_date):
        return True

# Graph 1
@app.callback(
    Output("heatmap-graph", "figure"),
    Output("portfolio-table", "rowData"),
    # Output("bottom-grid-footer", "rowData"),
    Input("apply-filter", 'n_clicks'),
    State("clinic-dropdown","value"),
    State("admit-source-dropdown", "value"),
    State("datepicker","start_date"),
    State("datepicker","end_date"),
    # prevent_initial_call=True
    
)
def update_heatmap(n_clicks, clinic, admit_source, start_date, end_date):

    if n_clicks and clinic and admit_source and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        df_heat = (
            df
            .filter((pl.col("Clinic Name").is_in(clinic)) & (pl.col("Admit Source").is_in(admit_source)) & ((pl.col("Check-In Time").is_between(start,end))))
            .group_by(["wk_day","wk_day_name","hour_am_pm"])
            .agg(pl.col("Number of Records").sum())
            .fill_null(strategy='zero')
            .sort(["wk_day"],descending=True)
            .collect()
            # .pivot(values="Number of Records", index="wk_day_name", columns="hour_am_pm", aggregate_function="sum",sort_columns=True).fill_null(0)
        )
        df_heat = (
            pl.concat([df_std,df_heat])
            .group_by(pl.all().exclude("Number of Records"))
            .agg(pl.col("Number of Records").sum())
            .sort(["wk_day"], descending=True)
            .pivot(values="Number of Records", index="wk_day_name", columns="hour_am_pm", aggregate_function="sum",sort_columns=True).fill_null(0)
        )
        fig = px.imshow(df_heat.select(pl.all().exclude("wk_day_name")),
                        text_auto=True,
                        x=df_heat.columns[1:],
                        y=df_heat.select(pl.col("wk_day_name")).to_series().to_list(),
                        color_continuous_scale=[[0, "#caf3ff"], [1, "#2c82ff"]],
                        # template="plotly_dark",
                        # labels={"x":"Horário","y":"Dia da Semana"}
                        )
        fig.update_xaxes(side="top")
        fig.update_traces(hovertemplate="<b> %{y} %{x} <br><br> %{z} Patient Records",name="")
        fig.update_layout(layout)
        fig.update_coloraxes(showscale=False)
        # =============== AG Grid - Table===============
        df_scatter = (
            df
            .filter((pl.col("Clinic Name").is_in(clinic)) & (pl.col("Admit Source").is_in(admit_source)) & ((pl.col("Check-In Time").is_between(start,end))))
            .group_by(["Department","Encounter Number"])
            .agg([
                pl.col("Wait Time Min").mean(),
                pl.col("Care Score").mean(),
                pl.col("wk_day").first(),
                pl.col("Check-In Time").first(),
                pl.col("hour").first()
            ])
        .select(
            [
                pl.col("Department"),
                pl.struct(pl.all().exclude("Department")).alias("my_struct")
                ]
            )
        .group_by("Department")
        .agg(pl.col("my_struct"))
        .sort("Department")
        .collect()
        )
        data = []
        for dp in df_scatter.select("Department").to_series():
            df_unnested = df_scatter.filter(pl.col("Department")==dp).explode("my_struct").unnest("my_struct")
            fig_await_time = px.scatter(df_unnested, x="Wait Time Min", y="Department",
                            height=60, #width=1000,
                            custom_data=["Encounter Number","Wait Time Min","Care Score","wk_day","Check-In Time","hour"])
                            # hover_data={"Encounter Number":True,"Wait Time Min":False,"Care Score":True,"wk_day":True,"Check-In Time":True })
            fig_await_time.update_traces(trace, marker_size=15,hovertemplate="Patient # : %{customdata[0]}<br>Check-In Time: %{customdata[4]} %{customdata[5]}<br>Wait Time Min: %{customdata[1]:.1f}  Care Score: %{customdata[2]:.1f}")
            fig_await_time.update_layout(layout_table,scattermode="group", scattergap=0.25,xaxis={"automargin": True})
            fig_await_time.update_yaxes(visible=False)
            fig_await_time.update_xaxes(visible=False, showline=False, showticklabels=True, tick0=0, dtick=20,range=[(df_unnested.select(pl.col("Wait Time Min").min()).item()-2.0), (df_unnested.select(pl.col("Wait Time Min").max()).item()+2.0)])
            # fig_await_time.update_xaxes(visible=False, showline=False, showticklabels=True, tick0=0, dtick=20,range=[-9, 194])

            #====
            fig_care_score = px.scatter(df_unnested, x="Care Score", y="Department",
                            height=60, #width=400,
                            custom_data=["Encounter Number","Wait Time Min","Care Score","wk_day","Check-In Time","hour"])
                            # hover_data={"Encounter Number":True,"Wait Time Min":False,"Care Score":True,"wk_day":True,"Check-In Time":True })
            fig_care_score.update_traces(trace, marker_size=15,hovertemplate="Patient # : %{customdata[0]}<br>Check-In Time: %{customdata[4]} %{customdata[5]}<br>Wait Time Min: %{customdata[1]:.1f}  Care Score: %{customdata[2]:.1f}")
            fig_care_score.update_layout(layout_table,scattermode="group", scattergap=0.25,xaxis={"automargin": True})
            fig_care_score.update_yaxes(visible=False)
            # fig_care_score.update_xaxes(visible=False, showline=False, showticklabels=True, tick0=0,range=[0,10])
            fig_care_score.update_xaxes(visible=False, showline=False, showticklabels=True, tick0=0,range=[(df_unnested.select(pl.col("Care Score").min()).item()-0.5), (df_unnested.select(pl.col("Care Score").max()).item()+0.5)])

            data.append({"Department":dp, "Wait Time Minutes":fig_await_time,"Care Score": fig_care_score})
        subset = pl.DataFrame(data)
        return fig, subset.to_dicts()#, bottomData

    else:
        df_st = (
            df_std
            .sort(["wk_day"], descending=True)
            .pivot(values="Number of Records", index="wk_day_name", columns="hour_am_pm", aggregate_function="sum",sort_columns=True).fill_null(0)
        )
        fig = px.imshow(df_st.select(pl.all().exclude("wk_day_name")),
                        text_auto=True,
                        x=df_st.columns[1:],
                        y=df_st.select(pl.col("wk_day_name")).to_series().to_list(),
                        color_continuous_scale=[[0, "#caf3ff"], [1, "#2c82ff"]],
                        # template="plotly_dark",
                        # labels={"x":"Horário","y":"Dia da Semana"}
                        )
        fig.update_xaxes(side="top")
        fig.update_traces(hovertemplate="<b> %{y} %{x} <br><br> %{z} Patient Records",name="")
        fig.update_layout(layout)
        fig.update_coloraxes(showscale=False)      
        return fig, []#, []

if __name__ == '__main__':
    app.run_server(host='localhost', port=8050, debug=False)