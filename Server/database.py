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

    @lru_cache()
    def regions(self, language="EN"):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(f"SELECT {language}_names FROM regions").fetchall()
        regions_names = []
        for region in result:
            regions_names.append(region[0])
        db.close()
        return regions_names

    @lru_cache()
    def translate_to_eng(self, region):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(
            f"""SELECT EN_names FROM regions
                            WHERE RU_names = \"{region}\"
        """
        ).fetchall()
        db.close()
        return result[0][0]

    @lru_cache()
    def coordinate(self, region):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(
            f"""SELECT X_coordinate, Y_coordinate FROM regions
                            WHERE (RU_names = \"{region}\"
                            OR EN_names = \"{region}\")
        """
        ).fetchall()
        db.close()
        return [result[0][0], result[0][1]]

    @lru_cache()
    def number_of_samples(self, region, first_date="default", last_date="default"):
        db = sqlite3.connect(Path("samples_data.db"))
        if first_date == "default":
            first_date = self.min_date
        if last_date == "default":
            last_date = self.max_date
        result = db.execute(
            f"""SELECT COUNT(*) FROM samples_data
                            WHERE (Location_RU = \"{region}\"
                            OR Location_EN = \"{region}\")
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
    def mutations_names(self):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(f"SELECT mutation_name FROM mutations").fetchall()
        mutations_names = []
        for region in result:
            mutations_names.append(region[0])
        db.close()
        return mutations_names

    @lru_cache()
    def info_about_mutation(self, mutation, lang):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(
            f"""SELECT {lang}_header, {lang}_info FROM mutations
                WHERE mutation_name = \"{mutation}\"
        """
        ).fetchall()
        db.close()
        return [result[0][0], result[0][1]]

    @lru_cache()
    def welcome_text(self, lang):
        db = sqlite3.connect(Path("samples_data.db"))
        result = db.execute(
            f"""SELECT text_body_{lang} FROM information_text
                WHERE text_name = "welcome"
        """
        ).fetchall()
        db.close()
        result = list(result)[0][0]
        return result

    def add_mutation_info(self, mutation, info, lang):
            db = sqlite3.connect(Path("samples_data.db"))
            db.execute(
                f"""UPDATE mutations
                    SET {lang}_info = {info}
                    WHERE mutation_name = {mutation};
            """
            )
            db.commit()
            db.close()
            return

    def add_mutation_info(self, mutation, info, lang):
            db = sqlite3.connect(Path("samples_data.db"))
            db.execute(
                f"""UPDATE mutations
                    SET {lang}_info = {info}
                    WHERE mutation_name = {mutation};
            """
            )
            db.commit()
            db.close()
            return
