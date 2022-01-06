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
    Div,
    Legend,
)
from bokeh.models.tools import HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
from bokeh.palettes import Category20, Colorblind
from datetime import date, datetime
import time
from functools import lru_cache
from settings import PLT_HEIGHT, PLT_WIDTH


def get_most_spread_variants(db, min_date, max_date, number):
    start_time = time.time()
    mutations = db.mutations_names
    number_of_samples = db.number_of_samples(first_date=min_date, last_date=max_date)
    if number_of_samples == 0:
        return []
    #print("gmsv.samples recieved --- %s seconds ---" % (time.time() - start_time))
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
            #print("gmsv.mutation parsed --- %s seconds ---" % (time.time() - start_time))
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
    start_time = time.time()
    first_y_label = db.get_text(lang, "first_y_label", "plot_information")
    second_y_label = db.get_text(lang, "second_y_label", "plot_information")
    other = db.get_text(lang, "other_text", "plot_information")
    min_date = datetime.strptime(min_date, '%Y-%m-%d').strftime("%Y-%m")
    max_date = datetime.strptime(max_date, '%Y-%m-%d').strftime("%Y-%m")
    datelist = pd.date_range(min_date, max_date, freq="MS").strftime("%Y-%m").tolist()
    samplelist = [db.number_of_samples_by_month(date) for date in datelist]
    data = {"dates": datelist}
    lineages = get_most_spread_variants(db, min_date, max_date, 15)
    if len(lineages) == 0:
        no_data_div = Div(text="No data", width=PLT_WIDTH, height=PLT_HEIGHT)
        return no_data_div
    print("most spread variants recieved --- %s seconds ---" % (time.time() - start_time))
    length = len(datelist)
    for lineage in lineages:
        data[lineage] = [0 for i in range(length)]
    data[other] = [0 for i in range(length)]
    for i in range(length):
        number_of_samples = samplelist[i]
        date = datelist[i]
        if number_of_samples == 0:
            for lineage in lineages:
                data[lineage][i] = 0
            data[other][i] = 0
            continue
        other_freq = 100
        for lineage in lineages:
            mutated_samples = db.number_of_mutated_variants_by_month(
                "lineage:" + lineage, date
            )
            freq = mutated_samples * 100 / number_of_samples
            other_freq -= freq
            data[lineage][i] = freq
        data[other][i] = other_freq
    lineages.append(other)
    colors = Category20[16]
    print("data formated --- %s seconds ---" % (time.time() - start_time))
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
    height= max(samplelist) + 100
    p.extra_y_ranges = {"number_of_samples": Range1d(start=0, end=height)}
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
    p.legend.background_fill_alpha = 0.1
    p.legend.items = p.legend.items[::-1]
    if width <= 1400:
        p.xaxis.major_label_orientation = pi/3
    if width <= 500:
        p.yaxis.axis_label = None
        p.plot_height = PLT_HEIGHT * 2
        p.legend.label_text_font_size = '10px'
    else:
        p.legend.label_text_font_size = '15px'
    p.legend.orientation = "vertical"
    p.add_layout(p.legend[0], "left")
    layout = column(p, sizing_mode="scale_width")
    print("finished --- %s seconds ---" % (time.time() - start_time))
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
    nonmutated_legend_text = db.get_text(lang, "legend_nonmutated", "plot_information")
    mutated_legend_text = db.get_text(lang, "legend_mutated", "plot_information")
    mutated_renders = []
    nonmutated_renders = []
    for region in db.regions(lang):
        coordinates_of_region = db.coordinate(region)
        all_variants = db.number_of_samples(region, min_date, max_date)
        if all_variants == 0:
            p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.1,
                start_angle=0,
                end_angle=2*pi,
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
            mr = p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                start_angle=0,
                end_angle=2*pi,
                line_width=0,
                fill_color=first_color,
                name=tooltip,
            )
            mutated_renders.append(mr)
        elif mutated_variants == 0:
            nmr = p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                alpha=0.8,
                start_angle=0,
                end_angle=2*pi,
                line_width=0,
                fill_color=second_color,
                name=tooltip,
            )
            nonmutated_renders.append(nmr)
        else:
            first_angle = mutated_variants / all_variants * 2 * pi
            second_angle = nonmutated_variants / all_variants * 2 * pi
            mr = p.wedge(
                x=coordinates_of_region[0],
                y=PLT_HEIGHT - coordinates_of_region[1],
                radius=10,
                start_angle=0,
                fill_color=first_color,
                end_angle=first_angle,
                line_width=0,
                name=tooltip,
                alpha=0.8,
            )
            nmr = p.wedge(
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
            nonmutated_renders.append(nmr)
            mutated_renders.append(mr)
    p.add_layout(Legend(items=[
    (nonmutated_legend_text, nonmutated_renders),
    (mutated_legend_text, mutated_renders),
    ]))
    p.legend.location = "top_left"
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
