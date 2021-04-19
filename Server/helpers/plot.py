from math import log2, pi

from functools import lru_cache
from bokeh.layouts import column, row
from bokeh.models import Paragraph, Select, Button, CustomJS
from bokeh.models.tools import HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
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
        toolbar_location="right",
        sizing_mode="scale_width",
        margin=[0, 0, 0, 90],
    )
    p.grid.visible = False
    p.axis.visible = False
    p.outline_line_color = "green"
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


def create_main_map(db, lang):
    p = configure_plot()
    for region in db.regions(lang):
        coordinates_of_region = db.coordinate(region)
        number_of_samples = db.number_of_samples(region)
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


def create_map(db, mutation_name, lang):
    p = configure_plot()
    if lang == "RU":
        no_data_text = "данные отсутсвуют"
    else:
        no_data_text = "no data"
    for region in db.regions(lang):
        coordinates_of_region = db.coordinate(region)
        all_variants = db.number_of_samples(region)
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
        mutated_variants = db.number_of_mutatated_variants(mutation_name, region)
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


def create_controls(db, lang, address="http://localhost:5006"):
    if lang == "RU":
        titles = ["Мутация", "Число образцов по регионам"]
        welcome_text = "Приветствуем на сайте coronomap! Вы можете выбрать мутацию и посмотреть как много образцов в каждом регионе или же вы можете посмотреть сколько образцов было получено в каждом регионе"
        lang_sw = "EN"
    else:
        titles = ["Mutation", "Number of samples per region"]
        welcome_text = "Welcome to coronomap website! You can choose mutation and see how many samples are presented in each region of Russion Federation or you can see how many samples were recieved in each region"
        lang_sw = "RU"
    mutations_names = db.mutations_names
    select = Select(
        min_height=50,
        title=titles[0],
        value=mutations_names[0],
        options=mutations_names,
        margin=[0, 100, 0, 100],
    )
    button = Button(
        min_height=50, label=titles[1], button_type="success", margin=[50, 25, 0, 100]
    )
    text = Paragraph(
        text=welcome_text,
        css_classes=["welcome_text"],
        margin=[50, 100, 0, 100],
    )
    lang_switch = Button(
        min_height=50, label=lang, button_type="success", margin=[50, 100, 0, 25]
    )
    select.js_on_change(
        "value",
        CustomJS(
            code=f"window.location.href=('{address}/?mutation=' + this.value + '&lang={lang}')"
        ),
    )
    button.js_on_click(
        CustomJS(code=f"window.location.href=('{address}/?mutation=ALL&lang={lang}')")
    )
    lang_switch.js_on_click(
        CustomJS(
            code=f"""var url_string = window.location.href;
                                              var url = new URL(url_string);
                                              var mutation = url.searchParams.get("mutation");
                                              window.location.href=(`{address}/?mutation=${{mutation}}&lang={lang_sw}`)"""
        )
    )
    controls = row(
        column(row(button, lang_switch), select), text, sizing_mode="scale_width"
    )
    return controls
