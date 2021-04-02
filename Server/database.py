import sqlite3
from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import _app_ctx_stack, current_app
from loguru import logger
from rich import print


class Database(object):
    """
    TODO: https://flask.palletsprojects.com/en/1.1.x/extensiondev/
    """

    def __init__(self, app=None):
        self.app = app
        self.min_date = "2020-01-01 00:00:00"
        self.max_date = "2021-02-09 00:00:00"

    @property
    @lru_cache()
    def regions(self):
        # FIXME: hardcode !
        file_for_regions = open(Path("Data", "regions.txt"), "r")
        return file_for_regions.read().split(",")

    @property
    @lru_cache()
    def mutation_names(self):
        mutations_names = (
            open(Path("Data", "mutations_names.txt"), "r").read().split(",")
        )

    # FIXME: hardcode !
    @property
    @lru_cache()
    def _data(self):
        file_for_data = open(Path("Data", "data.csv"), "r")
        return pd.read_csv(file_for_data, header=0)

    @lru_cache()
    def data_by_region(self, region):
        file_for_data = open(Path("Data", "data.csv"), "r")
        data = pd.read_csv(file_for_data, header=0)
        return data.loc[data["location"] == region]

    @lru_cache()
    def number_of_samples(self, region, first_date="default", last_date="default"):
        db = sqlite3.connect(Path("samples_data.db"))
        if first_date == "default":
            first_date = self.min_date
        if last_date == "default":
            last_date = self.max_date
        result = db.execute(
            f"""SELECT COUNT(*) FROM samples_data
                            WHERE Location = \"{region}\"
                            AND Date <= \"{last_date}\"
                            AND Date >= \"{first_date}\";
        """
        )
        result = int(list(result)[0][0])
        db.close()
        return result

    @lru_cache()
    def number_of_mutatated_variants(
        self, mutation, region, first_date="default", last_date="default"
    ):
        db = sqlite3.connect(Path("samples_data.db"))
        if first_date == "default":
            first_date = self.min_date
        if last_date == "default":
            last_date = self.max_date
        result = db.execute(
            f"""SELECT COUNT(*) FROM data_about_mutations
                            WHERE Mutation = \"{mutation}\"
                            AND (Location_RU = \"{region}\"
                            OR Location_EN = \"{region}\")
                            AND Date <= \"{last_date}\"
                            AND Date >= \"{first_date}\";
        """
        )
        result = int(list(result)[0][0])
        db.close()

        return result

    @property
    @lru_cache()
    def mutation_names(self):
        mutations_names = (
            open(Path("Data", "mutations_names.txt"), "r").read().split(",")
        )
        return mutations_names

    @property
    @lru_cache()
    def _information_about_mutations(self):
        information_about_mutations_raw = (
            open(Path("Data", "information_about_mutations.txt"), "r")
            .read()
            .split("\n")
        )
        information_about_mutations = {}
        for mutation_index in range(0, len(information_about_mutations_raw) - 1, 2):
            mutation_name = information_about_mutations_raw[mutation_index]
            information_about_mutation = information_about_mutations_raw[
                mutation_index + 1
            ]
            information_about_mutations[mutation_name] = information_about_mutation
        return information_about_mutations

    def mutation_info(self, mutation):
        return self._information_about_mutations[mutation]

    @property
    @lru_cache()
    def mutation_with_info_names(self):
        return self._information_about_mutations.keys()
