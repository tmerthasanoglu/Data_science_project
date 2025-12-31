import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
#-------------------------------
#DATA PATH
#-------------------------------
DATA_PATH = "../data-orders/data"


#-------------------------------
#LOAD DATA
#-------------------------------
orders = pd.read_csv(f"{DATA_PATH}/olist_orders_dataset.csv")
reviews = pd.read_csv(f"{DATA_PATH}/olist_order_reviews_dataset.csv")
items = pd.read_csv(f"{DATA_PATH}/olist_order_items_dataset.csv")

# -------------------
# PREPROCESS
# -------------------
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])

orders["delay_vs_expected"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.days.clip(lower=5)

orders["wait_time"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.days.clip(lower=5)

items_agg = (
items
.groupby("order_id", as_index=False)
.agg({"freight_value": "sum"})
)




df = (
 orders
.merge(reviews, on="order_id",how="left")
.merge(items_agg, on="order_id", how="left")
)


df["wait_bin"] = pd.cut(
    df["wait_time"],
    bins=[0, 5, 10, 20, 60],
    labels=["0–5 days", "6–10 days", "11–20 days", "20+ days"]
)

df["freight_bin"] = pd.cut(
    df["freight_value"],
    bins=[0, 10, 30, 100, 500],
    labels=["Low", "Medium", "High", "Very High"]
)

wait_summary = (
 df
    .groupby("wait_bin", as_index=False)
    .agg({"review_score": "mean"})
)

freight_summary = (
    df
    .groupby("freight_bin", as_index=False)
    .agg({"review_score": "mean"})
)





# -------------------
# FIGURE
# -------------------


fig_wait = px.bar(
    wait_summary,
    x="wait_bin",
    y="review_score",
    color="wait_bin",
    title="Average Review Score by Delivery Time"
        
    #labels={"review_score": "Avg Review Score", "wait_bin": "Delivery Time"}
)

fig_wait.update_layout(
    template="plotly_white",
    title={"x": 0.5},
    xaxis_title="Delivery Time (Days)",
    yaxis_title="Average Review Score"
)

fig_wait.update_traces(
    texttemplate="%{y:.2f}",
    textposition="outside"
)



fig_freight = px.bar(
    freight_summary,
    x="freight_bin",
    y="review_score",
    color="freight_bin",
    title="Average Review Score by Freight Cost"
)


fig_freight.update_layout(
    template="plotly_white",
    title={
        "text": "Average Review Score by Freight Cost",
        "x": 0.5
    },
    xaxis_title="Freight Cost Category",
    yaxis_title="Average Review Score",
    showlegend=False
)

fig_freight.update_traces(
    texttemplate="%{y:.2f}",
    textposition="outside"
)


# -------------------
# DASH APP
# -------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Olist Delivery Performance Dashboard",
        style={"textAlign": "center"}
    ),

  html.P(
        "How delivery performance impacts customer satisfaction",
        style={"textAlign": "center", "color": "red"}
    ),
    




    html.Div([

        html.Div(
            dcc.Graph(figure=fig_wait),
            style={"width": "48%", "display": "inline-block"}
        ),

        html.Div(
            dcc.Graph(figure=fig_freight),
            style={"width": "48%", "display": "inline-block"}
        ),

    ], style={"display": "flex", "justifyContent": "space-between"})

])

# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
