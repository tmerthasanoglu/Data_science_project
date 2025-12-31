import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, dash_table

# -------------------
# App
# -------------------
app = Dash(__name__)

# -------------------
# Data
# -------------------
df = pd.read_csv("data/sellers.csv")

# -------------------
# Layout
# -------------------
app.layout = html.Div(
    style={"width": "90%", "margin": "auto"},
    children=[

        html.H1("Seller Performance Dashboard"),

        html.P(
            "Olist satıcılarının teslimat süresi ve müşteri değerlendirmelerine göre analizi."
        ),

        # Controls
        html.Div(
            style={"display": "flex", "gap": "20px", "alignItems": "center"},
            children=[

                dcc.Dropdown(
                    id="state-dropdown",
                    options=[{"label": "All States", "value": "ALL"}] + [
                        {"label": state, "value": state}
                        for state in sorted(df["seller_state"].unique())
                    ],
                    value="ALL",
                    clearable=False,
                    style={"width": "200px"}
                ),

                dcc.Checklist(
                    id="bad-seller-check",
                    options=[
                        {"label": "Sadece kötü satıcılar (review < 4)", "value": "bad"}
                    ],
                    value=[]
                )
            ]
        ),

        html.Br(),

        # KPI Cards
        html.Div(
            id="kpi-cards",
            style={"display": "flex", "gap": "20px"}
        ),

        html.Br(),

        # Graphs
        dcc.Graph(id="review-vs-wait-time"),
        dcc.Graph(id="orders-distribution"),
        dcc.Graph(id="review-distribution"),

        html.H3("Worst Sellers (Top 10)"),

        dash_table.DataTable(
            id="worst-sellers-table",
            columns=[
                {"name": "Seller ID", "id": "seller_id"},
                {"name": "State", "id": "seller_state"},
                {"name": "Review Score", "id": "review_score"},
                {"name": "Wait Time", "id": "wait_time"},
                {"name": "Orders", "id": "n_orders"},
            ],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
        )
    ]
)

# -------------------
# Callback
# -------------------
@app.callback(
    Output("kpi-cards", "children"),
    Output("review-vs-wait-time", "figure"),
    Output("orders-distribution", "figure"),
    Output("review-distribution", "figure"),
    Output("worst-sellers-table", "data"),
    Input("state-dropdown", "value"),
    Input("bad-seller-check", "value")
)
def update_dashboard(selected_state, bad_filter):

    if selected_state == "ALL":
        filtered_df = df.copy()
    else:
        filtered_df = df[df["seller_state"] == selected_state]

    if "bad" in bad_filter:
        filtered_df = filtered_df[filtered_df["review_score"] < 4]

    # --- KPI calculations ---
    avg_review = round(filtered_df["review_score"].mean(), 2)
    avg_wait = round(filtered_df["wait_time"].mean(), 2)
    seller_count = filtered_df.shape[0]
    bad_ratio = round((filtered_df["review_score"] < 4).mean() * 100, 1)

    kpi_style = {
        "padding": "20px",
        "borderRadius": "10px",
        "backgroundColor": "#f5f5f5",
        "textAlign": "center",
        "width": "200px"
    }

    kpis = [
        html.Div([html.H4("Avg Review"), html.H2(avg_review)], style=kpi_style),
        html.Div([html.H4("Avg Wait Time"), html.H2(f"{avg_wait} days")], style=kpi_style),
        html.Div([html.H4("Bad Seller %"), html.H2(f"%{bad_ratio}")], style=kpi_style),
        html.Div([html.H4("Seller Count"), html.H2(seller_count)], style=kpi_style),
    ]

    # --- Graphs ---
    fig_scatter = px.scatter(
        filtered_df,
        x="wait_time",
        y="review_score",
        size="sales",
        color="delay_to_carrier",
        opacity=0.6,
        title="Wait Time vs Review Score"
    )

    fig_orders = px.histogram(
        filtered_df,
        x="n_orders",
        nbins=30,
        title="Order Count Distribution"
    )

    fig_reviews = px.histogram(
        filtered_df,
        x="review_score",
        nbins=10,
        title="Review Score Distribution"
    )

    # --- Worst sellers table ---
    worst_sellers = (
        filtered_df[filtered_df["review_score"] < 4]
        .sort_values("review_score")
        .head(10)
    )

    return (
        kpis,
        fig_scatter,
        fig_orders,
        fig_reviews,
        worst_sellers.to_dict("records")
    )

# -------------------
# Run
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
