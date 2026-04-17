from pathlib import Path

import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px


DATA_PATH = Path("data/formatted_output.csv")
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")


def load_sales_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"])
    return df


def prepare_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    daily_sales = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )
    return daily_sales


def build_figure(daily_sales: pd.DataFrame):
    fig = px.line(
        daily_sales,
        x="Date",
        y="Sales",
        title="Daily Pink Morsel Sales",
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales (USD)",
        template="plotly_white",
    )
    price_increase_date = PRICE_INCREASE_DATE.strftime("%Y-%m-%d")
    fig.add_shape(
        type="line",
        x0=price_increase_date,
        x1=price_increase_date,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line={"color": "red", "width": 2, "dash": "dash"},
    )
    fig.add_annotation(
        x=price_increase_date,
        y=1,
        xref="x",
        yref="paper",
        text="Price increase (2021-01-15)",
        showarrow=False,
        xanchor="left",
    )
    return fig


sales_df = load_sales_data(DATA_PATH)
daily_sales_df = prepare_daily_sales(sales_df)

avg_sales_before = daily_sales_df.loc[
    daily_sales_df["Date"] < PRICE_INCREASE_DATE, "Sales"
].mean()
avg_sales_after = daily_sales_df.loc[
    daily_sales_df["Date"] >= PRICE_INCREASE_DATE, "Sales"
].mean()
comparison_text = (
    "Average daily sales were higher after the price increase."
    if avg_sales_after > avg_sales_before
    else "Average daily sales were higher before the price increase."
)

app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    [
        html.H1("Soul Foods Pink Morsel Sales Visualiser"),
        html.P("Daily total sales over time, with the 2021-01-15 price increase marked."),
        dcc.Graph(figure=build_figure(daily_sales_df)),
        html.H3(comparison_text),
    ],
    style={"maxWidth": "1000px", "margin": "0 auto", "padding": "24px"},
)


if __name__ == "__main__":
    app.run(debug=False)
