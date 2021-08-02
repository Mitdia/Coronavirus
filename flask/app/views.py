from app import app
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
    create_plot,
    create_main_map,
    create_map,
    create_date_range_slider,
)
from helpers.security import security_check
from helpers.template import get_template_variables
from jinja2 import Environment, PackageLoader, Template
from loguru import logger
from settings import SERVER_ADDRESS, SERVER_PORT

db = Database(app)

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


@app.route("/map")
def map():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    min_date = request.args.get("min_date", default="2020-02-01", type=str)
    max_date = request.args.get("max_date", default="2021-02-09", type=str)
    if not security_check(db, mutation, language, min_date, max_date):
        return flask.render_template("error.html")
    if mutation == "ALL":
        p = create_main_map(db, language, min_date, max_date)
    elif mutation in db.mutations_names:
        p = create_map(db, mutation, language, min_date, max_date)
    return json_item(p, "coronamap")


@app.route("/plot")
def plot():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    min_date = request.args.get("min_date", default="2020-02-01", type=str)
    max_date = request.args.get("max_date", default="2021-02-09", type=str)
    window_size = request.args.get("window_width", type=int)
    if not security_check(db, mutation, language, min_date, max_date):
        return flask.render_template("error.html")
    if mutation == "ALL":
        p = create_plot(db, language, min_date, max_date, window_size)
    return json_item(p, "coronaplot")


@app.route("/dateRangeSlider")
def date_range_slider():
    mutation = request.args.get("mutation", default="ALL", type=str)
    language = request.args.get("lang", default="EN", type=str)
    min_date = request.args.get("min_date", default="2020-01-01", type=str)
    max_date = request.args.get("max_date", default="2021-02-09", type=str)
    if not security_check(db, mutation, language, min_date, max_date):
        return flask.render_template("error.html")
    p = create_date_range_slider(mutation, language, min_date, max_date)
    return json_item(p, "dateRangeSlider")


@app.route("/embed")
def embed_map():
    today = datetime.today().strftime("%Y-%m-%d")
    mutation = request.args.get("mutation", type=str)
    language = request.args.get("lang", type=str)
    min_date = request.args.get("min_date", type=str)
    max_date = request.args.get("max_date", type=str)
    if not security_check(db, mutation, language, min_date, max_date):
        return redirect(
            f"/embed?mutation=ALL&lang=RU&min_date=2020-2-9&max_date={today}"
        )
    template_variables = get_template_variables(db, mutation, language, min_date, max_date)
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
        template=app.jinja_env.get_template("embed.html"),
        template_variables=template_variables,
    )


@app.route("/home")
def home():
    today = datetime.today().strftime("%Y-%m-%d")
    mutation = request.args.get("mutation", type=str)
    language = request.args.get("lang", type=str)
    min_date = request.args.get("min_date", type=str)
    max_date = request.args.get("max_date", type=str)
    if not security_check(db, mutation, language, min_date, max_date):
        return redirect(
            f"/home?mutation=ALL&lang=RU&min_date=2020-2-9&max_date={today}"
        )
    template_variables = get_template_variables(
        db, mutation, language, min_date, max_date
    )
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
        template=app.jinja_env.get_template("index.html"),
        template_variables=template_variables,
    )


@app.route("/")
def root():
    today = datetime.today().strftime("%Y-%m-%d")
    mutation = request.args.get("mutation", type=str)
    language = request.args.get("lang", type=str)
    min_date = request.args.get("min_date", type=str)
    max_date = request.args.get("max_date", type=str)
    if not security_check(db, mutation, language, min_date, max_date):
        return redirect(
            f"/home?mutation=ALL&lang=RU&min_date=2020-2-9&max_date={today}"
        )
    template_variables = get_template_variables(
        db, mutation, language, min_date, max_date
    )
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
        template=app.jinja_env.get_template("index.html"),
        template_variables=template_variables,
    )
