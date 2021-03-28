from math import log2, pi, sqrt
from pathlib import Path

import pandas as pd
from bokeh.embed import file_html
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import Button, CustomJS, Dropdown, Paragraph, Select
from bokeh.models.tools import *
from bokeh.plotting import figure, output_file
from bokeh.server.server import Server
from bokeh.settings import settings

import map_data

PLT_WIDTH = 1500
PLT_HEIGHT = 866
settings.resources = "inline"
settings.log_level = "debug"


def init():
    global data, regions, mutations_names, information_about_mutations
    file_for_data = open(Path("Data", "data.csv"), "r")
    file_for_regions = open(Path("Data", "regions.txt"), "r")
    file_for_mutations_names = open(Path("Data", "mutations_names.txt"), "r")
    file_for_information_about_mutations = open(
        Path("Data", "information_about_mutations.txt"), "r"
    )
    data = pd.read_csv(file_for_data, header=0)
    regions = file_for_regions.read().split(",")
    mutations_names = file_for_mutations_names.read().split(",")
    information_about_mutations_raw = file_for_information_about_mutations.read().split(
        "\n"
    )
    information_about_mutations = {}
    for mutation_index in range(0, len(information_about_mutations_raw) - 1, 2):
        mutation_name = information_about_mutations_raw[mutation_index]
        information_about_mutation = information_about_mutations_raw[mutation_index + 1]
        information_about_mutations[mutation_name] = information_about_mutation


def configure_plot():
    zoom = WheelZoomTool(zoom_on_axis=False)
    reset = ResetTool()
    hover = HoverTool()
    pan = PanTool()
    TOOLTIPS = """
        <div>
            <span style="font-size: 20px; ">$name</span>
        </div>
    """
    tools = [zoom, reset, hover, pan]
    p = figure(
        plot_width=PLT_WIDTH,
        plot_height=PLT_HEIGHT,
        tooltips=TOOLTIPS,
        tools=tools,
        toolbar_location="right",
        margin=[0, 100, 0, 100],
    )
    p.grid.visible = False
    p.axis.visible = False
    p.outline_line_color = "green"
    p.match_aspect = True
    p.toolbar.active_scroll = zoom
    p.image_url(
        url=["https://ma.fbb.msu.ru/coronamap/static/map.svg"],
        x=0,
        y=0,
        w=PLT_WIDTH,
        h=PLT_HEIGHT,
        anchor="bottom_left",
    )
    return p


def create_main_map():
    p = configure_plot()
    for region in regions:
        coordinates_of_region = map_data.coordinates[region]
        number_of_samples = (data.location == region).sum()
        radius = log2(number_of_samples + 1) * 5
        p.circle(
            x=coordinates_of_region[0],
            y=PLT_HEIGHT - coordinates_of_region[1],
            radius=radius,
            alpha=0.5,
            fill_color="blue",
            name=f"{region}: {number_of_samples}",
        )
    return p


def create_map(mutation_name, data):
    p = configure_plot()
    for region in regions:
        coordinates_of_region = map_data.coordinates[region]
        region_data = data.loc[data["location"] == region]
        all_variants = len(region_data)
        if all_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.1,
                fill_color="blue",
                name=f"{region}: данные отсутсвуют",
            )
            continue
        mutated_variants = region_data[mutation_name].sum()
        nonmutated_variants = all_variants - mutated_variants
        if nonmutated_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                fill_color="red",
                name=f"{region}: {int(mutated_variants)}/{all_variants}",
            )
        elif mutated_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                fill_color="green",
                name=f"{region}: {int(mutated_variants)}/{all_variants}",
            )
        else:
            first_angle = mutated_variants / all_variants * 2 * pi
            second_angle = nonmutated_variants / all_variants * 2 * pi
            first_color = "red"
            second_color = "green"
            first_name = f"{region}: {int(mutated_variants)}/{all_variants}"
            p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                start_angle=0,
                fill_color=first_color,
                end_angle=first_angle,
                line_color="white",
                name=first_name,
                alpha=0.8,
            )
            p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                start_angle=first_angle,
                fill_color=second_color,
                end_angle=(second_angle + first_angle),
                line_color="white",
                name=first_name,
                alpha=0.8,
            )
    return p


def render_text(mutation_name):
    information_about_mutation = information_about_mutations[mutation_name]
    text = Paragraph(
        text=information_about_mutation,
        width=(PLT_WIDTH // 2),
        height=PLT_HEIGHT,
        margin=[0, 100, 0, 100],
    )
    return text


def update_plot(attrname, old, new):
    global last_module, data, doc
    mutation = select.value
    doc.remove_root(last_module)
    if mutation in information_about_mutations:
        text = render_text(mutation)
        map = create_map(mutation, data)
        last_module = column(map, text, sizing_mode="scale_width")
    else:
        map = create_map(mutation, data)
        last_module = column(map, sizing_mode="scale_width")
    doc.add_root(last_module)


def show_main_map():
    global last_module, data, doc
    doc.remove_root(last_module)
    last_module = column(create_main_map(), sizing_mode="scale_width")
    doc.add_root(last_module)


def run(doc):
    select = Select(
        min_height=50,
        title="Mutation",
        value=mutations_names[0],
        options=mutations_names,
        margin=[0, 0, 0, 100],
    )
    button = Button(
        min_height=50,
        label="Number of samples per regions",
        button_type="success",
        margin=[0, 0, 0, 100],
    )
    select.on_change("value", update_plot)
    button.on_click(show_main_map)
    controls = column(button, select)
    last_module = column(create_main_map(), sizing_mode="scale_width")
    doc = curdoc()

    doc.title = "Coronavirus"
    doc.add_root(controls)
    doc.add_root(last_module)


def test(doc):
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]

    fig = figure(title="simple line example", x_axis_label="x", y_axis_label="y")
    fig.line(x, y, legend="Temp.", line_width=2)

    layout = column(fig)
    doc.add_root(layout)


if __name__ == "__main__":
    init()
    print("init complete")
    kws = {
        "address": "0.0.0.0",
        "port": 5006,
        "prefix": "/bokeh",
        "allow_websocket_origin": ["*"],
    }
    server = Server(test, **kws)
    # server = Server(run, **kws)
    server.start()
    if __name__ == "__main__":
        server.io_loop.add_callback(server.show, "/")
        server.io_loop.start()
