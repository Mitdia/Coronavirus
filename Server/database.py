import functools
import json
import random
import sqlite3
import sys
from functools import lru_cache, partial
from math import log2, pi, sqrt
from pathlib import Path

import click
import pandas as pd
from bokeh.embed import components, file_html, json_item
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (BoxAnnotation, Button, CustomJS, Dropdown, Paragraph,
                          Select)
from bokeh.models.tools import *
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN, INLINE
from bokeh.sampledata.iris import flowers
from bokeh.server.server import Server
# from bokeh.settings import settings
from flask import Flask, _app_ctx_stack, current_app, g, render_template
from flask.cli import with_appcontext
from jinja2 import Environment, PackageLoader, Template
from loguru import logger
from rich import print
from settings import (PLT_HEIGHT, PLT_WIDTH, SERVER_ADDRESS,
                      SERVER_ALLOW_WEBSOCKET_ORIGIN, SERVER_PORT,
                      SERVER_PREFIX)

import map_data


class Database(object):
    """
    https://flask.palletsprojects.com/en/1.1.x/extensiondev/
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('SQLITE3_DATABASE', ':memory:')
        app.teardown_appcontext(self.teardown)

    def connect(self):
        return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'sqlite3_db'):
            ctx.sqlite3_db.close()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db = self.connect()
            return ctx.sqlite3_db

    #----------------------------------------------------------
    #----------------------------------------------------------
    #----------------------------------------------------------
    #----------------------------------------------------------
    #----------------------------------------------------------
    #----------------------------------------------------------
    # вот тут пусть все эти наши функции будут
    @property
    @lru_cache()
    def regions(self):
        file_for_regions = open(Path("Data", "regions.txt"), "r")
        return file_for_regions.read().split(",")

    @lru_cache()
    def data_by_region(self, region):
        file_for_data = open(Path("Data", "data.csv"), "r")
        data = pd.read_csv(file_for_data, header=0)
        return data.loc[data["location"] == region].copy()
