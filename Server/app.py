import sys
from functools import lru_cache

from bokeh.embed import file_html, json_item
from bokeh.plotting import figure
from bokeh.models import Paragraph
from bokeh.resources import CDN
from database import Database
from flask import Flask, request
from helpers.plot import create_main_map, create_map
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
    mutation = request.args.get("mutation", default = "all", type=str)
    if mutation == "all":
        p = create_main_map(db)
    elif mutation in db.mutation_names:
        p = create_map(db, mutation)
    return json_item(p, "coronaplot")


@app.route("/")
def root():
    mutation = request.args.get("mutation", default = "all", type=str)
    return file_html(
        # [controls, last_module],
        [figure(), Paragraph()],  # TODO: remove me CDN only
        CDN,
        "Coronavirus",
        template=jinja_env.get_template("index.html"),
        template_variables={"mutation": mutation}
    )


if __name__ == "__main__":
    app.run(
        host=SERVER_ADDRESS,
        port=SERVER_PORT,
        # debug=False,
        debug=True,
    )
