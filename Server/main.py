# noinspection PyInterpreter
import pandas as pd
import map_data
from bokeh.plotting import figure, output_file
from bokeh.io import show, curdoc
from math import pi
from bokeh.models import CustomJS, Select, Panel, Tabs, Dropdown, Button
from bokeh.layouts import column, row
from math import sqrt, log2



def parser_demo():
    main_data = open("Data\\DecemberFinalForMap.merged_pangolin_lineages.WithAncNodes.csv", 'r')
    mutations_data = open("Data\\RUSSIA.INTERESTING_VARIANTS.COUCCURRENCE.JAN.txt", 'r')
    parsed_data = pd.read_csv(main_data, sep=';', header=0)
    data_about_mutations = pd.read_csv(mutations_data, sep='\t', header=0)
    parsed_data.set_index("GISAID_name")
    data_about_mutations.set_index("GISAID_name")
    parsed_data = parsed_data.merge(data_about_mutations, how='left')
    parsed_data.where(pd.notnull(parsed_data), 0)
    main_data.close()
    mutations_data.close()
    return parsed_data


def get_mutations_names():
    mutations_data = open("Data\\RUSSIA.INTERESTING_VARIANTS.COUCCURRENCE.JAN.txt", 'r')
    data_about_mutations = pd.read_csv(mutations_data, sep='\t', header=0)
    parsed_mutation_names = []
    for pd_column in data_about_mutations.columns[1:]:
        parsed_mutation_names.append(pd_column)
    return parsed_mutation_names


def create_main_map():
    global plt_width, plt_height
    p = figure(plot_width=plt_width, plot_height=plt_height, tooltips="$name", tools="pan,wheel_zoom,reset")
    p.image_url(url=[' http://localhost:5006/Server/static/map.svg'], x=0, y=0, w=plt_width, h=plt_height,
                anchor="bottom_left")
    for region in regions:
        coordinates_of_region = map_data.coordinates[region]
        number_of_samples = (data.location == region).sum()
        radius = log2(number_of_samples + 1) * 5
        p.circle(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=radius, alpha=0.5,
                     fill_color="blue",
                     name=f"{region}: {number_of_samples}")
    return p


def create_map(mutation_name, data):
    global plt_width, plt_height
    p = figure(plot_width=plt_width, plot_height=plt_height, tooltips="$name", tools="pan,wheel_zoom,reset")
    p.image_url(url=[' http://localhost:5006/Server/static/map.svg'], x=0, y=0, w=plt_width, h=plt_height, anchor="bottom_left")
    for region in regions:
        coordinates_of_region = map_data.coordinates[region]
        region_data = data.loc[data['location'] == region]
        all_variants = len(region_data)
        if all_variants == 0:
            p.circle(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=10, alpha=0.1,
                     fill_color="blue",
                     name=f"{region}: данные отсутсвуют")
            continue
        mutated_variants = region_data[mutation_name].sum()
        nonmutated_variants = all_variants - mutated_variants
        if nonmutated_variants == 0:
            p.circle(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=10, alpha=0.8,
                     fill_color="red",
                     name=f"{region}: {int(mutated_variants)}/{all_variants}")
        elif mutated_variants == 0:
            p.circle(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=10, alpha=0.8,
                     fill_color="green",
                     name=f"{region}: {int(mutated_variants)}/{all_variants}")
        else:
            first_angle = mutated_variants / all_variants * 2 * pi
            second_angle = nonmutated_variants / all_variants * 2 * pi
            first_color = 'red'
            second_color = 'green'
            first_name = f'{region}: {int(mutated_variants)}/{all_variants}'
            p.wedge(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=10,
                    start_angle=0, fill_color=first_color, end_angle=first_angle, line_color="white", name=first_name,
                    alpha=0.8)
            p.wedge(x=coordinates_of_region[0], y=plt_height - coordinates_of_region[1], radius=10,
                    start_angle=first_angle, fill_color=second_color, end_angle=(second_angle + first_angle),
                    line_color="white", name=first_name, alpha=0.8)
    return p


def update_plot(attrname, old, new):
    global last_module, data
    mutation = select.value
    curdoc().remove_root(last_module)
    last_module = row(create_map(mutation, data))
    curdoc().add_root(last_module)


def show_main_map():
    global last_module, data
    curdoc().remove_root(last_module)
    last_module = row(create_main_map())
    curdoc().add_root(last_module)


plt_width = 1500
plt_height = 866
file_for_data = open("Data\\data.csv", 'r')
file_for_regions = open("Data\\regions.txt", 'r')
file_for_mutations_names = open("Data\\mutations_names.txt", 'r')
data = pd.read_csv(file_for_data, header=0)
regions = file_for_regions.read().split(',')
mutations_names = file_for_mutations_names.read().split(',')
select = Select(title="Мутация", value=mutations_names[0], options=mutations_names)
button = Button(label="Количество образцов по регионам", button_type="success")
select.on_change('value', update_plot)
button.on_click(show_main_map)
controls = column(button, select)
last_module = row(create_main_map())
curdoc().title = 'Coronavirus'
curdoc().add_root(controls)
curdoc().add_root(last_module)

