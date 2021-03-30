from math import log2, pi

from bokeh.layouts import column
from bokeh.models import Paragraph, Select
from bokeh.models.tools import HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
from settings import PLT_HEIGHT, PLT_WIDTH

from .map_data import coordinates


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
        sizing_mode="scale_width",
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


def create_main_map(db):
    p = configure_plot()
    for region in db.regions:
        coordinates_of_region = coordinates[region]
        number_of_samples = db.data_by_region_sum(region)
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


def create_map(db, mutation_name, data):
    p = configure_plot()
    for region in db.regions:
        coordinates_of_region = coordinates[region]
        region_data = db.data_by_region(region)

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


def render_text(db, mutation_name):
    information_about_mutation = db.mutation_info(name)
    text = Paragraph(
        text=information_about_mutation,
        width=(PLT_WIDTH // 2),
        height=PLT_HEIGHT,
        margin=[0, 100, 0, 100],
    )
    return text


def update_plot(db, attrname, old, new, doc):
    global last_module, data
    mutation = select.value
    doc.remove_root(last_module)
    if mutation in db.mutation_names:
        text = render_text(mutation)
        map = create_map(mutation, data)
        last_module = column(map, text, sizing_mode="scale_width")
    else:
        map = create_map(mutation, data)
        last_module = column(map, sizing_mode="scale_width")
    doc.add_root(last_module)


def show_main_map(doc):
    global last_module, data
    doc.remove_root(last_module)
    last_module = column(create_main_map(), sizing_mode="scale_width")
    doc.add_root(last_module)
