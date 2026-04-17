from pathlib import Path
import sys

from dash import dcc, html
from dash.development.base_component import Component

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app as dash_app


def walk_components(component):
    if isinstance(component, Component):
        yield component
        children = getattr(component, "children", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                yield from walk_components(child)
        elif children is not None:
            yield from walk_components(children)


def test_header_is_present():
    headers = [
        component
        for component in walk_components(dash_app.layout)
        if isinstance(component, html.H1)
    ]

    assert headers
    assert headers[0].children == "Soul Foods Pink Morsel Sales Visualiser"


def test_visualisation_is_present():
    graphs = [
        component
        for component in walk_components(dash_app.layout)
        if isinstance(component, dcc.Graph)
    ]

    assert graphs
    assert any(graph.id == "sales-chart" for graph in graphs)


def test_region_picker_is_present():
    radio_items = [
        component
        for component in walk_components(dash_app.layout)
        if isinstance(component, dcc.RadioItems)
    ]

    assert radio_items
    region_picker = next(item for item in radio_items if item.id == "region-filter")

    option_values = {option["value"] for option in region_picker.options}
    assert option_values == {"north", "east", "south", "west", "all"}
