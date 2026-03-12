## Stephen Locke
## March 12 2026


#!/usr/bin/env python3
"""
FRED Economic Data Interactive Dashboard
Uses the fedfred library to search, filter, and visualize FRED data.

Requirements:
    pip install fedfred dash dash-bootstrap-components plotly pandas openpyxl

Usage:
    Set the FRED_API_KEY environment variable OR enter it in the dashboard.
    Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html

    python fred_dashboard.py
    Then open: http://127.0.0.1:8050
"""

import os
from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import fedfred as fd
import plotly.graph_objects as go
from dash import Input, Output, State, dash_table, dcc, html

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="FRED Economic Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

TRACE_COLORS = ["#1a6fc4", "#e05c2d", "#2ca02c"]


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

app.layout = dbc.Container(
    fluid=True,
    children=[
        # ── Header ────────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("FRED Economic Data Dashboard", className="mb-0"),
                        html.P(
                            "Search and plot Federal Reserve Economic Data",
                            className="text-muted mb-0",
                        ),
                    ],
                    className="py-3 border-bottom mb-3",
                )
            )
        ),
        # ── API Key ────────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("API Key", className="card-title text-uppercase text-muted small"),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("FRED API Key"),
                                    dbc.Input(
                                        id="api-key-input",
                                        #type="password",
                                        placeholder="Paste your key here (or set FRED_API_KEY env var)",
                                        value=os.environ.get("FRED_API_KEY", ""),
                                        debounce=False,
                                    ),
                                ]
                            ),
                            html.Small(
                                [
                                    "Get a free key at ",
                                    html.A(
                                        "fred.stlouisfed.org",
                                        href="https://fred.stlouisfed.org/docs/api/api_key.html",
                                        target="_blank",
                                    ),
                                ],
                                className="text-muted",
                            ),
                        ]
                    ),
                    className="mb-3 shadow-sm",
                ),
                width=12,
            )
        ),
        # ── Search ─────────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "Search Series",
                                className="card-title text-uppercase text-muted small",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            id="search-input",
                                            type="text",
                                            placeholder='e.g. "unemployment rate", "GDP", "CPI", "housing starts"',
                                        ),
                                        width=12,
                                        md=9,
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            [html.I(className="me-2"), "Search"],
                                            id="search-button",
                                            color="primary",
                                            className="w-100",
                                            n_clicks=0,
                                        ),
                                        width=12,
                                        md=3,
                                    ),
                                ],
                                className="g-2",
                            ),
                        ]
                    ),
                    className="mb-3 shadow-sm",
                ),
                width=12,
            )
        ),
        # ── Results Table ──────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "Search Results",
                                className="card-title text-uppercase text-muted small",
                            ),
                            dbc.Spinner(
                                [
                                    html.Div(
                                        id="search-status",
                                        className="text-muted small mb-2",
                                        children="Enter a search term above to find series.",
                                    ),
                                    dash_table.DataTable(
                                        id="results-table",
                                        columns=[
                                            {"name": "Series ID", "id": "id", "presentation": "markdown"},
                                            {"name": "Title", "id": "title"},
                                            {"name": "Freq.", "id": "frequency"},
                                            {"name": "Units", "id": "units"},
                                            {"name": "Seasonal Adj.", "id": "seasonal_adjustment"},
                                            {"name": "Last Updated", "id": "last_updated"},
                                        ],
                                        data=[],
                                        row_selectable="multi",
                                        selected_rows=[],
                                        style_table={
                                            "overflowX": "auto",
                                            "maxHeight": "300px",
                                            "overflowY": "auto",
                                        },
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "8px 12px",
                                            "fontSize": "13px",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                            "maxWidth": "320px",
                                        },
                                        style_header={
                                            "backgroundColor": "#f4f6f8",
                                            "fontWeight": "600",
                                            "borderBottom": "2px solid #dee2e6",
                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {"row_index": "odd"},
                                                "backgroundColor": "#f9fbfd",
                                            },
                                            {
                                                "if": {"state": "selected"},
                                                "backgroundColor": "#cce5ff",
                                                "border": "1px solid #0066cc",
                                            },
                                        ],
                                        tooltip_data=[],
                                        tooltip_delay=0,
                                        tooltip_duration=None,
                                        page_action="none",
                                    ),
                                ],
                                color="primary",
                                size="sm",
                            ),
                        ]
                    ),
                    className="mb-3 shadow-sm",
                ),
                width=12,
            )
        ),
        # ── Chart Controls ─────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "Chart Options",
                                className="card-title text-uppercase text-muted small",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Start Date", className="small fw-semibold"),
                                            dbc.Input(
                                                id="start-date",
                                                type="date",
                                                value=(
                                                    datetime.now() - timedelta(days=365 * 10)
                                                ).strftime("%Y-%m-%d"),
                                            ),
                                        ],
                                        width=12,
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("End Date", className="small fw-semibold"),
                                            dbc.Input(
                                                id="end-date",
                                                type="date",
                                                value=datetime.now().strftime("%Y-%m-%d"),
                                            ),
                                        ],
                                        width=12,
                                        md=3,
                                    ),
                                ],
                                className="g-2 align-items-end",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button(
                                            "Plot Selected Series (up to 3)",
                                            id="plot-button",
                                            color="success",
                                            className="mt-3",
                                            n_clicks=0,
                                        ),
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Export to Excel",
                                            id="export-button",
                                            color="secondary",
                                            outline=True,
                                            className="mt-3",
                                            n_clicks=0,
                                        ),
                                        width="auto",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    className="mb-3 shadow-sm",
                ),
                width=12,
            )
        ),
        # ── Main Chart ─────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dbc.Spinner(
                                dcc.Graph(
                                    id="main-chart",
                                    style={"height": "480px"},
                                    config={
                                        "displayModeBar": True,
                                        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                                        "toImageButtonOptions": {
                                            "format": "png",
                                            "filename": "fred_chart",
                                            "height": 600,
                                            "width": 1200,
                                        },
                                    },
                                ),
                                color="success",
                            )
                        ]
                    ),
                    className="mb-3 shadow-sm",
                ),
                width=12,
            )
        ),
        # ── Series Info ────────────────────────────────────────────────────
        dbc.Row(dbc.Col(html.Div(id="series-info"), width=12)),
        # ── Hidden stores ──────────────────────────────────────────────────
        dcc.Store(id="search-results-store"),
        dcc.Store(id="selected-series-store"),
        dcc.Download(id="excel-download"),
    ],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_record(obj) -> dict:
    """Convert a fedfred result object or dict to a plain JSON-serializable dict."""
    import dataclasses
    if isinstance(obj, dict):
        d = obj
    elif dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        d = {f.name: getattr(obj, f.name) for f in dataclasses.fields(obj)}
    else:
        for method in ("model_dump", "dict"):
            if hasattr(obj, method):
                d = getattr(obj, method)()
                break
        else:
            d = vars(obj)
    # Drop non-serializable fields (e.g. the fedfred client reference)
    return {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool, type(None)))}


def _make_fred(api_key: str) -> fd.FredAPI:
    return fd.FredAPI(api_key=api_key)


def _empty_figure(message: str = "") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message or "Select a series and click 'Plot Selected Series'",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 16, "color": "#6c757d"},
            }
        ],
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


# ---------------------------------------------------------------------------
# Callback: Search
# ---------------------------------------------------------------------------

@app.callback(
    Output("search-results-store", "data"),
    Output("results-table", "data"),
    Output("results-table", "tooltip_data"),
    Output("results-table", "selected_rows"),
    Output("search-status", "children"),
    Input("search-button", "n_clicks"),
    State("search-input", "value"),
    State("api-key-input", "value"),
    prevent_initial_call=True,
)
def search_series(n_clicks, search_text, api_key):
    api_key = (api_key or "").strip()
    if not api_key:
        return [], [], [], [], dbc.Alert("Please enter a FRED API key.", color="warning", className="py-1 mb-0")
    if not search_text or not search_text.strip():
        return [], [], [], [], dbc.Alert("Please enter a search term.", color="warning", className="py-1 mb-0")

    try:
        fred = _make_fred(api_key)

        raw_results = fred.get_series_search(
            search_text=search_text.strip(),
            limit=100,
            order_by="search_rank",
            sort_order="desc",
        )

        if not raw_results:
            return [], [], [], [], "No results found."

        records = [_to_record(r) for r in raw_results]

        table_data = []
        tooltip_data = []
        for rec in records:
            last_updated = str(rec.get("last_updated", ""))[:10]
            freq = rec.get("frequency_short") or rec.get("frequency") or ""
            units = rec.get("units_short") or rec.get("units") or ""
            seas = rec.get("seasonal_adjustment_short") or rec.get("seasonal_adjustment") or ""
            title = rec.get("title", "")

            table_data.append(
                {
                    "id": rec.get("id", ""),
                    "title": title[:90] + ("…" if len(title) > 90 else ""),
                    "frequency": freq,
                    "units": units[:35] + ("…" if len(units) > 35 else ""),
                    "seasonal_adjustment": seas,
                    "last_updated": last_updated,
                }
            )
            tooltip_data.append(
                {
                    "title": {"value": title, "type": "text"},
                    "units": {"value": rec.get("units", ""), "type": "text"},
                }
            )

        status = html.Span(
            [
                html.Strong(f"{len(table_data)} series"),
                f" found for '{search_text.strip()}'",
                ". Click up to 3 rows to select them.",
            ]
        )
        return records, table_data, tooltip_data, [], status

    except Exception as exc:
        return [], [], [], [], dbc.Alert(f"Search error: {exc}", color="danger", className="py-1 mb-0")


# ---------------------------------------------------------------------------
# Callback: Select series from table
# ---------------------------------------------------------------------------

@app.callback(
    Output("selected-series-store", "data"),
    Input("results-table", "selected_rows"),
    State("search-results-store", "data"),
    prevent_initial_call=True,
)
def store_selected_series(selected_rows, search_results):
    if not selected_rows or not search_results:
        return []
    # Cap at 3 series (take the last 3 selected so the user can swap by clicking)
    rows = selected_rows[-3:]
    return [search_results[i] for i in rows if i < len(search_results)]


@app.callback(
    Output("start-date", "value"),
    Input("selected-series-store", "data"),
    prevent_initial_call=True,
)
def update_start_date(selected_series_list):
    if not selected_series_list:
        return dash.no_update
    if isinstance(selected_series_list, dict):
        selected_series_list = [selected_series_list]
    dates = [
        str(s.get("observation_start", "") or "")[:10]
        for s in selected_series_list
        if s.get("observation_start")
    ]
    if not dates:
        return dash.no_update
    return min(dates)


# ---------------------------------------------------------------------------
# Callback: Plot series
# ---------------------------------------------------------------------------

def _effective_unit_label(series_meta: dict, units_transform: str) -> str:
    """Return the display label for a series' y-axis given the applied transform."""
    transform_labels = {
        "chg": "Change",
        "ch1": "Change from Year Ago",
        "pch": "% Change",
        "pc1": "% Change (YoY)",
        "log": "Log",
    }
    if units_transform and units_transform != "lin":
        return transform_labels.get(units_transform, units_transform)
    return series_meta.get("units_short") or series_meta.get("units") or "Value"


@app.callback(
    Output("main-chart", "figure"),
    Output("series-info", "children"),
    Input("plot-button", "n_clicks"),
    State("selected-series-store", "data"),
    State("start-date", "value"),
    State("end-date", "value"),
    State("api-key-input", "value"),
    prevent_initial_call=True,
)
def plot_series(n_clicks, selected_series_list, start_date, end_date, api_key):
    api_key = (api_key or "").strip()
    if not selected_series_list:
        return _empty_figure("Select up to 3 series from the results table first."), ""
    if not api_key:
        return _empty_figure("Enter a FRED API key."), ""

    # Normalise: accept both a single dict (legacy) and a list
    if isinstance(selected_series_list, dict):
        selected_series_list = [selected_series_list]
    selected_series_list = selected_series_list[:3]

    fred = _make_fred(api_key)
    fig = go.Figure()
    info_rows = []
    errors = []

    # First pass: fetch all series so we can determine unique units
    fetched = []  # list of (series_meta, df, y_label)
    for series_meta in selected_series_list:
        series_id = series_meta.get("id", "")
        try:
            obs_kwargs = dict(
                series_id=series_id,
                observation_start=start_date,
                observation_end=end_date,
            )
            df = fred.get_series_observations(**obs_kwargs)

            if df is None or len(df) == 0:
                errors.append(f"No observations returned for {series_id}.")
                continue

            y_label = _effective_unit_label(series_meta, "lin")
            fetched.append((series_meta, df, y_label))
        except Exception as exc:
            errors.append(f"Error loading {series_id}: {exc}")

    if not fetched:
        msg = " | ".join(errors) if errors else "No data returned."
        return _empty_figure(msg), dbc.Alert(msg, color="danger", className="mb-3")

    # Determine axis assignment: first unique unit → yaxis, second → yaxis2
    seen_units: list[str] = []
    for _, _, y_label in fetched:
        if y_label not in seen_units:
            seen_units.append(y_label)

    dual_axis = len(seen_units) >= 2

    for i, (series_meta, df, y_label) in enumerate(fetched):
        series_id = series_meta.get("id", "")
        color = TRACE_COLORS[i % len(TRACE_COLORS)]

        y_col = "value" if "value" in df.columns else df.columns[-1]
        x_values = df.index
        y_values = df[y_col]

        axis_idx = seen_units.index(y_label)  # 0 → yaxis, 1 → yaxis2
        yaxis_ref = "y" if axis_idx == 0 else "y2"

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                name=series_id,
                yaxis=yaxis_ref,
                line=dict(color=color, width=2),
                hovertemplate=(
                    f"<b>{series_id}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    f"{y_label}: %{{y:,.4f}}<extra></extra>"
                ),
            )
        )

        # Build series info row
        obs_count = len(df)
        date_range = f"{str(x_values[0])[:10]} → {str(x_values[-1])[:10]}"
        info_rows.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                style={"width": "12px", "height": "12px", "backgroundColor": color,
                                       "display": "inline-block", "borderRadius": "50%", "marginRight": "6px"},
                            ),
                            html.Strong(series_id, className="small"),
                            html.Small([" — ", series_meta.get("title", "")], className="text-muted d-block mt-1"),
                            html.Small([html.Strong("Units: "), series_meta.get("units", "")], className="d-block"),
                            html.Small([html.Strong("Frequency: "), series_meta.get("frequency", "")], className="d-block"),
                            html.Small([html.Strong("Seasonal Adj.: "), series_meta.get("seasonal_adjustment", "")], className="d-block"),
                            html.Small([html.Strong("Last Updated: "), str(series_meta.get("last_updated", ""))[:10]], className="d-block"),
                            html.Small([html.Strong("Observations: "), f"{obs_count:,}"], className="d-block"),
                            html.Small([html.Strong("Date Range: "), date_range], className="d-block"),
                        ]
                    ),
                    className="shadow-sm bg-light h-100",
                ),
                width=12,
                md=4,
            )
        )

    # Build chart title from series IDs
    chart_title = " vs ".join(sm.get("id", "") for sm, _, _ in fetched)

    yaxis_cfg = dict(
        title=seen_units[0],
        showgrid=True,
        gridcolor="#ececec",
        zeroline=False,
    )
    layout_extra = {}
    if dual_axis:
        layout_extra["yaxis2"] = dict(
            title=seen_units[1],
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        )
        # Shrink right margin to make room for right-axis label
        r_margin = 80
    else:
        r_margin = 30

    fig.update_layout(
        title=dict(text=f"<b>{chart_title}</b>", font=dict(size=15), x=0.02),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#ececec", zeroline=False),
        yaxis=yaxis_cfg,
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=60, r=r_margin, t=70, b=60),
        **layout_extra,
    )

    info_card = dbc.Card(
        dbc.CardBody(
            [
                html.H6("Series Information", className="card-title text-uppercase text-muted small"),
                dbc.Row(info_rows, className="g-2"),
                *(
                    [dbc.Alert(" | ".join(errors), color="warning", className="mt-2 mb-0 py-1 small")]
                    if errors else []
                ),
            ]
        ),
        className="mb-3 shadow-sm",
    )

    return fig, info_card


# ---------------------------------------------------------------------------
# Callback: Export to Excel
# ---------------------------------------------------------------------------

@app.callback(
    Output("excel-download", "data"),
    Input("export-button", "n_clicks"),
    State("selected-series-store", "data"),
    State("start-date", "value"),
    State("end-date", "value"),
    State("api-key-input", "value"),
    prevent_initial_call=True,
)
def export_excel(_n_clicks, selected_series_list, start_date, end_date, api_key):
    import io
    import pandas as pd

    api_key = (api_key or "").strip()
    if not selected_series_list or not api_key:
        return dash.no_update

    if isinstance(selected_series_list, dict):
        selected_series_list = [selected_series_list]
    selected_series_list = selected_series_list[:3]

    fred = _make_fred(api_key)
    frames = {}       # series_id → Series
    meta_rows = []    # one dict per series for the info sheet

    INFO_FIELDS = [
        ("Series ID",           "id"),
        ("Title",               "title"),
        ("Units",               "units"),
        ("Frequency",           "frequency"),
        ("Seasonal Adjustment", "seasonal_adjustment"),
        ("Last Updated",        "last_updated"),
        ("Notes",               "notes"),
    ]

    for series_meta in selected_series_list:
        series_id = series_meta.get("id", "")
        try:
            obs_kwargs = dict(series_id=series_id)

            df = fred.get_series_observations(**obs_kwargs)
            if df is None or len(df) == 0:
                continue

            y_col = "value" if "value" in df.columns else df.columns[-1]
            frames[series_id] = df[y_col].rename(series_id)

            meta_rows.append({label: str(series_meta.get(key, "") or "") for label, key in INFO_FIELDS})
        except Exception:
            continue

    if not frames:
        return dash.no_update

    # Data sheet: date index + one column per series
    data_df = pd.concat(frames.values(), axis=1)
    data_df.index = pd.to_datetime(data_df.index).strftime("%Y-%m-%d")
    data_df.index.name = "Date"

    # Info sheet
    info_df = pd.DataFrame(meta_rows).T.reset_index()
    info_df.columns = ["Field"] + [f"Series {i + 1}" for i in range(len(meta_rows))]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        info_df.to_excel(writer, sheet_name="Series Info", index=False)
        data_df.to_excel(writer, sheet_name="Data")

    ids = "_".join(frames.keys())
    filename = f"fred_{ids}_{start_date}_to_{end_date}.xlsx"

    return dcc.send_bytes(buf.getvalue(), filename)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print(f"\n  FRED Dashboard running at http://127.0.0.1:{port}\n")
    app.run(debug=False, port=port)
