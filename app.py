from pathlib import Path

import dash
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px


DATA_PATH = Path("data/formatted_output.csv")
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")
REGION_OPTIONS = ["all", "north", "east", "south", "west"]


def load_sales_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"])
    df["Region"] = df["Region"].str.strip().str.lower()
    return df


def prepare_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    daily_sales = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )
    return daily_sales


def filter_sales_by_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    if region == "all":
        return df
    return df[df["Region"] == region]


def format_region_label(region: str) -> str:
    return "All Regions" if region == "all" else region.title()


def build_figure(daily_sales: pd.DataFrame, region: str):
    region_label = format_region_label(region)
    fig = px.line(
        daily_sales,
        x="Date",
        y="Sales",
        title=f"Daily Pink Morsel Sales - {region_label}",
        markers=True,
        color_discrete_sequence=["#0b6e4f"],
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales (USD)",
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 40, "r": 25, "t": 70, "b": 45},
        title={"x": 0.03},
    )
    fig.update_traces(line={"width": 3}, marker={"size": 5})
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
        yshift=-10,
        font={"color": "#b23a48", "size": 12},
    )
    return fig


sales_df = load_sales_data(DATA_PATH)

app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    [
        html.Div(
            className="hero-card",
            children=[
                html.H1("Soul Foods Pink Morsel Sales Visualiser", className="app-title"),
                html.P(
                    "Explore daily sales by region and compare performance around the "
                    "2021-01-15 price increase.",
                    className="app-subtitle",
                ),
            ],
        ),
        html.Div(
            className="control-card",
            children=[
                html.Label("Select Region", className="control-label"),
                dcc.RadioItems(
                    id="region-filter",
                    options=[{"label": region, "value": region} for region in REGION_OPTIONS],
                    value="all",
                    inline=True,
                    className="region-radio",
                ),
            ],
        ),
        html.Div(
            className="chart-card",
            children=[
                dcc.Graph(id="sales-chart", className="sales-chart"),
            ],
        ),
        html.Div(id="comparison-text", className="insight-card"),
    ],
    className="page-shell",
)


@app.callback(
    Output("sales-chart", "figure"),
    Output("comparison-text", "children"),
    Input("region-filter", "value"),
)
def update_dashboard(selected_region: str):
    filtered_sales_df = filter_sales_by_region(sales_df, selected_region)
    daily_sales_df = prepare_daily_sales(filtered_sales_df)

    avg_sales_before = daily_sales_df.loc[
        daily_sales_df["Date"] < PRICE_INCREASE_DATE, "Sales"
    ].mean()
    avg_sales_after = daily_sales_df.loc[
        daily_sales_df["Date"] >= PRICE_INCREASE_DATE, "Sales"
    ].mean()
    comparison_text = (
        "higher after"
        if avg_sales_after > avg_sales_before
        else "higher before"
    )
    region_label = format_region_label(selected_region)
    insight = (
        f"{region_label}: average daily sales were {comparison_text} the price increase. "
        f"Before: ${avg_sales_before:,.2f} | After: ${avg_sales_after:,.2f}"
    )

    return build_figure(daily_sales_df, selected_region), insight


if __name__ == "__main__":
    app.run(debug=False)
