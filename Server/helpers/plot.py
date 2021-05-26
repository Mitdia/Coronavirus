from math import log2, pi

from functools import lru_cache
from bokeh.layouts import column, row
from bokeh.models import Paragraph, Select, Button, CustomJS, DateRangeSlider
from bokeh.models.tools import HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
from datetime import date
from settings import PLT_HEIGHT, PLT_WIDTH


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
        toolbar_location=None,
        sizing_mode="scale_width",
    )
    p.grid.visible = False
    p.axis.visible = False
    p.outline_line_width = 0
    p.match_aspect = True
    p.toolbar.active_scroll = zoom

    p.image_url(
        url=["/static/img/map.svg"],
        x=0,
        y=0,
        w=PLT_WIDTH,
        h=PLT_HEIGHT,
        anchor="bottom_left",
    )
    return p


def create_main_map(db, lang, min_date, max_date):
    p = configure_plot()
    for region in db.regions(lang):
        coordinates_of_region = db.coordinate(region)
        number_of_samples = db.number_of_samples(region, min_date, max_date)
        radius = log2(number_of_samples + 1) * 5
        p.circle(
            x=coordinates_of_region[0],
            y=PLT_HEIGHT - coordinates_of_region[1],
            radius=radius,
            alpha=0.5,
            fill_color="blue",
            name=f"{region}: {number_of_samples}",
        )
    layout = column(p, sizing_mode="scale_width")
    return layout


def create_map(db, mutation_name, lang, min_date, max_date):
    p = configure_plot()
    if lang == "RU":
        no_data_text = "данные отсутсвуют"
    else:
        no_data_text = "no data"
    for region in db.regions(lang):
        coordinates_of_region = db.coordinate(region)
        all_variants = db.number_of_samples(region, min_date, max_date)
        if all_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.1,
                fill_color="blue",
                name=f"{region}: {no_data_text}",
            )
            continue
        mutated_variants = db.number_of_mutatated_variants(
            mutation_name, region, min_date, max_date
        )
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

    layout = column(p, sizing_mode="scale_width")
    return layout


def create_date_range_slider(mutation_name, lang, min_date, max_date):
    mind = [int(i) for i in min_date.split("-")]
    maxd = [int(i) for i in max_date.split("-")]
    date_range_slider = DateRangeSlider(
        value=(date(mind[0], mind[1], mind[2]), date(maxd[0], maxd[1], maxd[2])),
        start=date(2019, 1, 1),
        end=date(2021, 12, 31),
        width_policy="max",
    )
    date_range_slider.js_on_change(
        "value",
        CustomJS(
            code=f"""
            var mutation = url.searchParams.get("mutation");
            var language = url.searchParams.get("lang");
            var max_date_previous = url.searchParams.get("max_date");
            var min_date_previous = url.searchParams.get("min_date");
            var updateDate = document.getElementById("updateDate");
            var min_timestamp = this.value[0];
            var max_timestamp = this.value[1];
            var min_date = new Date(min_timestamp);
            var str_min_date = min_date.getFullYear() + "-" + (min_date.getMonth() + 1) + "-" + min_date.getDate();
            var max_date = new Date(max_timestamp);
            var str_max_date = max_date.getFullYear() + "-" + (max_date.getMonth() + 1) + "-" + max_date.getDate();
            updateDate.onclick = function() {{window.location.href=(`/?mutation=${{mutation}}&lang=${{language}}&min_date=${{str_min_date}}&max_date=${{str_max_date}}`);}};
            var updateDateText = document.getElementById("updateDateText");
            updateDate.removeChild(updateDateText)
            var updateDateText = document.createElement("p");
            updateDateText.id = "updateDateText";
            updateDateText.textContent = `${{str_min_date}} - ${{str_max_date}}`;
            updateDate.appendChild(updateDateText)
            """
        ),
    )
    return column(date_range_slider, sizing_mode="scale_width")
