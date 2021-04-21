import sys
from functools import lru_cache
from pathlib import Path

from bokeh.embed import file_html, json_item
from bokeh.plotting import figure
from bokeh.models import Paragraph, Select, Button
from bokeh.resources import CDN
from database import Database
from flask import Flask, request, Markup, send_from_directory
from helpers.plot import create_main_map, create_map, create_select, create_lang_switch, create_home_button
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
    if mutation == "ALL":
        p = create_main_map(db, language)
    elif mutation in db.mutations_names:
        p = create_map(db, mutation, language)
    return json_item(p, "coronaplot")


@app.route("/controls")
def controls():
    language = request.args.get("lang", default="EN", type=str)
    p = create_controls(db, language)
    return json_item(p, "coronacontrols")


@app.route("/button")
def home_button():
    language = request.args.get("lang", default="EN", type=str)
    p = create_home_button(db, language)
    return json_item(p, "home_button")


@app.route("/lang_switch")
def lang_switch():
    language = request.args.get("lang", default="EN", type=str)
    p = create_lang_switch(db, language)
    return json_item(p, "language_switch")


@app.route("/select")
def select():
    language = request.args.get("lang", default="EN", type=str)
    p = create_select(db, language)
    return json_item(p, "select")


@app.route("/")
def root():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    if mutation not in db.mutations_names:
        mutation = "ALL"
    if language != "RU":
        language = "EN"
    mutation_info = db.info_about_mutation(mutation, language)
    mutation_info_header = mutation_info[0]
    mutation_info = mutation_info[1]
    welcome_text = db.welcome_text(language)
    return file_html(
        # [controls, last_module],
        [figure(), Paragraph(), Select(), Button()],  # TODO: remove me CDN only
        CDN,
        "Coronavirus",
        template=jinja_env.get_template("index.html"),
        template_variables={
            "mutation": mutation,
            "mutation_info_header": mutation_info_header,
            "mutation_info": mutation_info,
            "welcome_text": welcome_text,
            "lang": language,
        },
    )


if __name__ == "__main__":
    app.run(
        host=SERVER_ADDRESS,
        port=SERVER_PORT,
        # debug=False,
        debug=True,
    )
