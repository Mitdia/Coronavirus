import sys
from functools import lru_cache
from pathlib import Path
from datetime import date, datetime
from bokeh.embed import file_html, json_item
from bokeh.plotting import figure
from bokeh.models import DateRangeSlider
from bokeh.resources import CDN
from database import Database
from flask import Flask, request, Markup, send_from_directory, redirect
from helpers.plot import (
    create_main_map,
    create_map,
    create_date_range_slider,
    create_link_to_outbreak_info,
)
from helpers.security import check_date_format
from jinja2 import Environment, PackageLoader, Template
from loguru import logger
from settings import SERVER_ADDRESS, SERVER_PORT

app = Flask(__name__)
db = Database(app)
jinja_env = Environment(loader=PackageLoader("app", "templates"))

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


@app.route("/plot")
def plot():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    min_date = request.args.get("min_date", default="2020-02-01", type=str)
    max_date = request.args.get("max_date", default="2021-02-09", type=str)
    if mutation == "ALL":
        p = create_main_map(db, language, min_date, max_date)
    elif mutation in db.mutations_names:
        p = create_map(db, mutation, language, min_date, max_date)
    return json_item(p, "coronaplot")


@app.route("/dateRangeSlider")
def date_range_slider():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    min_date = request.args.get("min_date", default="2020-01-01", type=str)
    max_date = request.args.get("max_date", default="2021-02-09", type=str)
    p = create_date_range_slider(mutation, language, min_date, max_date)
    return json_item(p, "dateRangeSlider")


@app.route("/")
def root():
    today = datetime.today().strftime("%Y-%m-%d")
    mutation = request.args.get("mutation", type=str)
    language = request.args.get("lang", type=str)
    min_date = request.args.get("min_date", type=str)
    max_date = request.args.get("max_date", type=str)
    if (
        mutation == None
        or language == None
        or not check_date_format(min_date)
        or not check_date_format(max_date)
    ):
        return redirect(f"/?mutation=ALL&lang=EN&min_date=2020-2-9&max_date={today}")
    lang_sw = "EN"
    mutations_names = db.mutations_names[1:]
    if mutation not in mutations_names:
        mutation = "ALL"
    if language != "RU":
        language = "EN"
        lang_sw = "RU"
    mutation_info = db.info_about_mutation(mutation, language)
    mutation_info_header = mutation_info[0]
    mutation_info = mutation_info[1]
    welcome_text = db.get_text(language, "welcome")
    further_information_text = db.get_text(language, "further_information")
    home_button_text = db.get_text(language, "home_button")
    update_button_text = db.get_text(language, "update_button")
    mutation_choice_button_text = db.get_text(language, "mutation_choice_button")
    gene_choice_button_text = db.get_text(language, "gene_choice_button")
    variables_text = db.get_text(language, "variables")
    date_slider_text = db.get_text(language, "date_slider")
    outbreak_info_link = create_link_to_outbreak_info(mutation)

    template_variables = {
        "outbreak_info_link": outbreak_info_link,
        "update_button_text": update_button_text,
        "home_button_text": home_button_text,
        "mutation_choice_button_text": mutation_choice_button_text,
        "variables_text": variables_text,
        "date_slider_text": date_slider_text,
        "gene_choice_button_text": gene_choice_button_text,
        "mutation": mutation,
        "mutation_info_header": mutation_info_header,
        "mutation_info": mutation_info,
        "welcome_text": welcome_text,
        "further_information_text": further_information_text,
        "lang": language,
        "lang_sw": lang_sw,
        "mutations_names": mutations_names,
        "min_date": min_date,
        "max_date": max_date,
    }

    return file_html(
        # [controls, last_module],
        [
            figure(),
            DateRangeSlider(
                value=(date(2016, 1, 1), date(2016, 12, 31)),
                start=date(2015, 1, 1),
                end=date(2017, 12, 31),
            ),
        ],  # TODO: remove me CDN only
        CDN,
        "taxameter.ru",
        template=jinja_env.get_template("index.html"),
        template_variables=template_variables,
    )


if __name__ == "__main__":
    app.run(
        host=SERVER_ADDRESS,
        port=SERVER_PORT,
        debug=False,
    )
