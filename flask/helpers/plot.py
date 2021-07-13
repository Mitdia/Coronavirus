from math import log2, pi
import pandas as pd
from functools import lru_cache
from bokeh.layouts import column, row
from bokeh.models import (
    Paragraph,
    Select,
    Button,
    CustomJS,
    DateRangeSlider,
    Range1d,
    DatePicker,
    LinearAxis,
)
from bokeh.models.tools import HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
from bokeh.palettes import Category20, Colorblind
from datetime import date, datetime
from settings import PLT_HEIGHT, PLT_WIDTH


def get_most_spread_variants(db, min_date, max_date, number):
    mutations = db.mutations_names
    number_of_samples = db.number_of_samples(first_date=min_date, last_date=max_date)
    lineages = {}
    for mutation in mutations[1:]:
        lineage = mutation
        mutation = mutation.split(":")
        if mutation[0] == "lineage":
            freq = db.number_of_mutated_variants(lineage, first_date=min_date, last_date=max_date) / number_of_samples
            if len(lineages) < number:
                lineages[mutation[1]] = freq
                continue
            min_freq = min(lineages, key=lineages.get)
            if lineages[min_freq] < freq:
                del lineages[min_freq]
                lineages[mutation[1]] = freq
    return list(lineages.keys())


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
    p.x_range = Range1d(0, PLT_WIDTH, bounds="auto")
    p.y_range = Range1d(0, PLT_HEIGHT, bounds="auto")
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.min_border_left = 0
    p.min_border_right = 0
    p.min_border_top = 0
    p.min_border_bottom = 0
    p.outline_line_width = 0
    p.outline_line_color = None
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


def create_plot(db, lang, min_date, max_date, width):
    first_y_label = db.get_text(lang, "first_y_label", "plot_information")
    second_y_label = db.get_text(lang, "second_y_label", "plot_information")
    other = db.get_text(lang, "other_text", "plot_information")
    datelist = pd.date_range(min_date, max_date, freq="MS").strftime("%Y-%m").tolist()
    samplelist = [db.number_of_samples_by_month(date) for date in datelist]
    data = {"dates": datelist}
    lineages = get_most_spread_variants(db, min_date, max_date, 15)
    for lineage in lineages:
        data[lineage] = []
    data[other] = []
    for i in range(len(datelist)):
        number_of_samples = samplelist[i]
        date = datelist[i]
        if number_of_samples == 0:
            for lineage in lineages:
                data[lineage].append(0)
            data[other].append(0)
            continue
        other_freq = 100
        for lineage in lineages:
            mutated_samples = db.number_of_mutated_variants_by_month(
                "lineage:" + lineage, date
            )
            freq = mutated_samples * 100 / number_of_samples
            other_freq -= freq
            data[lineage].append(freq)
        data[other].append(other_freq)
    lineages.append(other)
    colors = Category20[16]
    p = figure(
        plot_width=PLT_WIDTH,
        plot_height=PLT_HEIGHT,
        x_range=data["dates"],
        tools=[],
        toolbar_location=None,
    )
    vbar_stack = p.vbar_stack(
        lineages, x="dates", width=0.9, color=colors, source=data, legend_label=lineages
    )
    if lang == "RU":
        hover = HoverTool(renderers=vbar_stack, tooltips=("Частота $name, @dates: @$name{1.1}%"))
    else:
        hover = HoverTool(renderers=vbar_stack, tooltips=("$name prevalence, @dates: @$name{1.1}%"))
    p.add_tools(hover)
    p.y_range.start = 0
    p.y_range = Range1d(0, 100)
    p.yaxis.axis_label = first_y_label
    p.extra_y_ranges = {"number_of_samples": Range1d(start=0, end=600)}
    p.add_layout(
        LinearAxis(y_range_name="number_of_samples", axis_label=second_y_label),
        "right",
    )
    p.line(
        datelist,
        samplelist,
        y_range_name="number_of_samples",
        color="black",
        line_width=3,
        name="number of samples",
    )
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_width = 0
    p.outline_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.background_fill_alpha = 0.1
    p.legend.items = p.legend.items[::-1]
    if width <= 920:
        p.xaxis.major_label_orientation = pi/3
        p.legend.items = []
    layout = column(p, sizing_mode="scale_width")
    return layout


def create_main_map(db, lang, min_date, max_date, mode="main"):
    p = configure_plot()
    most_prevaling_lineages_names = get_most_spread_variants(db, min_date, max_date, 5)
    for region in db.regions(lang):
        other = db.get_text(lang, "other_text", "plot_information")
        coordinates_of_region = db.coordinate(region)
        number_of_samples = db.number_of_samples(region, min_date, max_date)
        most_prevaling_lineages = {}
        for lineage in most_prevaling_lineages_names:
            line = "lineage:" + lineage
            number = db.number_of_mutated_variants(line, region, min_date, max_date)
            most_prevaling_lineages[lineage] = number
        if number_of_samples != 0:
            radius = log2(number_of_samples + 1) * 5
            name = f"{region}: {number_of_samples}"
            if mode == "main":
                other_number = number_of_samples
                for lineage in most_prevaling_lineages:
                    lineage_number = int(most_prevaling_lineages[lineage])
                    other_number -= lineage_number
                    lineage_freq = round(lineage_number / number_of_samples * 100, 1)
                    name += '<br>' + lineage + ' - ' + str(lineage_number) + ' (' + str(lineage_freq) + '%)'
                other_freq = round(other_number / number_of_samples * 100, 1)
                name += '<br>' + other + ' - ' + str(other_number) + ' (' + str(other_freq) + '%)'
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=radius,
                alpha=0.5,
                fill_color="blue",
                name=name,
            )
    layout = column(p, sizing_mode="scale_width")
    return layout


def create_map(db, mutation_name, lang, min_date, max_date):
    p = configure_plot()
    no_data_text = db.get_text(lang, "no_data_text", "plot_information")
    map_tooltip = db.get_text(lang, "map_tooltip", "plot_information")
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
        mutated_variants = db.number_of_mutated_variants(
            mutation_name, region, min_date, max_date
        )
        nonmutated_variants = all_variants - mutated_variants
        freq = round(mutated_variants / all_variants * 100, 1)
        tooltip = f"{region}: {mutated_variants} {map_tooltip} {all_variants} ({freq}%)"
        first_color = Colorblind[7][5]
        second_color = Colorblind[7][3]
        if nonmutated_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                fill_color=first_color,
                name=tooltip,
            )
        elif mutated_variants == 0:
            p.circle(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                fill_color=second_color,
                name=tooltip,
            )
        else:
            first_angle = mutated_variants / all_variants * 2 * pi
            second_angle = nonmutated_variants / all_variants * 2 * pi
            p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                start_angle=0,
                fill_color=first_color,
                end_angle=first_angle,
                line_color="white",
                name=tooltip,
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
                name=tooltip,
                alpha=0.8,
            )

    layout = column(p, sizing_mode="scale_width")
    return layout


def create_date_range_slider(mutation_name, lang, min_date, max_date):
    mind = [int(i) for i in min_date.split("-")]
    maxd = [int(i) for i in max_date.split("-")]
    # min_date_picker = DatePicker(title='Minimum date', value=date(mind[0], mind[1], mind[2]), min_date=date(2020, 2, 1), max_date=datetime.today().strftime("%Y-%m-%d"))
    # max_date_picker = DatePicker(title='Maximum date', value=date(maxd[0], maxd[1], maxd[2]), min_date=date(2020, 2, 1), max_date=datetime.today().strftime("%Y-%m-%d"))
    date_range_slider = DateRangeSlider(
        value=(date(mind[0], mind[1], mind[2]), date(maxd[0], maxd[1], maxd[2])),
        start=date(2020, 2, 1),
        end=datetime.today().strftime("%Y-%m-%d"),
        width_policy="max",
    )
    """
    min_date_picker.js_on_change(
        "value",
        CustomJS(code="minDatePicker(this.value)"),
    )
    min_date_picker.js_on_change(
        "value",
        CustomJS(code="maxDatePicker(this.value)"),
    )
    """
    date_range_slider.js_on_change(
        "value",
        CustomJS(code="dateRangeSlider(this.value[0], this.value[1])"),
    )
    # return column(row(min_date_picker, max_date_picker), date_range_slider, sizing_mode="scale_width")
    return column(date_range_slider, sizing_mode="scale_width")
