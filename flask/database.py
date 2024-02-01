import sqlite3
import time
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


class Database(object):
    """
    TODO: https://flask.palletsprojects.com/en/1.1.x/extensiondev/
    """

    def __init__(self, app=None):
        self.app = app
        today = datetime.today().strftime("%Y-%m-%d")
        self.min_date = "2020-02-01 00:00:00"
        self.max_date = f"{today} 00:00:00"

    @lru_cache()
    def regions(self, language="EN"):
        # start_time = time.time()
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(f"SELECT {language}_names FROM regions").fetchall()
        regions_names = []
        for region in result:
            regions_names.append(region[0])
        db.close()
        # print("db.regions --- %s seconds ---" % (time.time() - start_time))
        return regions_names

    @lru_cache()
    def translate_to_eng(self, region):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(
            f"""SELECT EN_names FROM regions
                            WHERE RU_names = \"{region}\"
        """
        ).fetchall()
        db.close()
        return result[0][0]

    @lru_cache()
    def coordinate(self, region):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(
            f"""SELECT X_coordinate, Y_coordinate FROM regions
                            WHERE (RU_names = \"{region}\"
                            OR EN_names = \"{region}\")
        """
        ).fetchall()
        db.close()
        return [result[0][0], result[0][1]]

    @lru_cache()
    def number_of_samples(self, region="ALL", first_date="default", last_date="default"):
        start_time = time.time()
        db = sqlite3.connect(Path("samples_data.sqlite"))
        if first_date == "default":
            first_date = self.min_date
        if last_date == "default":
            last_date = self.max_date
        format = "%Y-%m-%d"
        first_date = datetime.strptime(first_date, format)
        last_date = datetime.strptime(last_date, format)
        if region == "ALL":
            result = db.execute(
                f"""SELECT COUNT(*) FROM samples_data
                                WHERE Date <= \"{last_date}\"
                                AND Date >= \"{first_date}\";
            """
            )
        else:
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
        #print("db.number_of_samples --- %s seconds ---" % (time.time() - start_time))
        return result

    @lru_cache()
    def number_of_samples_by_month(self, date="ALL"):
        start_time = time.time()
        if date == "ALL":
            db = sqlite3.connect(Path("samples_data.sqlite"))
            result = db.execute(f"SELECT COUNT(*) FROM samples_data")
            result = int(list(result)[0][0])
            db.close()
        else:
            format = "%Y-%m-%d"
            first_date = datetime.strptime(date, "%Y-%m")
            last_date = last_day_of_month(first_date)
            first_date = datetime.strftime(first_date, format)
            last_date = datetime.strftime(last_date, format)
            result = self.number_of_samples("ALL", first_date, last_date)
        # print("db.number_of_samples_by_month --- %s seconds ---" % (time.time() - start_time))
        return result

    @lru_cache()
    def number_of_mutated_variants(
        self, mutation, region="ALL", first_date="default", last_date="default"
    ):
        # start_time = time.time()
        db = sqlite3.connect(Path("samples_data.sqlite"))
        if first_date == "default":
            first_date = self.min_date
        if last_date == "default":
            last_date = self.max_date
        format = "%Y-%m-%d"
        first_date = datetime.strptime(first_date, format)
        last_date = datetime.strptime(last_date, format)
        if mutation.split(":")[0] == "lineage":
            if region == "ALL":
                result = db.execute(
                    f"""SELECT COUNT(*) FROM samples_data
                                    WHERE lineage = \"{mutation}\"
                                    AND date <= \"{last_date}\"
                                    AND date >= \"{first_date}\";
                """
                )
            else:
                result = db.execute(
                    f"""SELECT COUNT(*) FROM samples_data
                                    WHERE lineage = \"{mutation}\"
                                    AND (Location_RU = \"{region}\"
                                    OR Location_EN = \"{region}\")
                                    AND date <= \"{last_date}\"
                                    AND date >= \"{first_date}\";
                """
                )
        else:

            if region == "ALL":
                result = db.execute(
                    f"""SELECT COUNT(*) FROM data_about_mutations
                                    WHERE Mutation = \"{mutation}\"
                                    AND Date <= \"{last_date}\"
                                    AND Date >= \"{first_date}\";
                """
                )
            else:
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
        # print("db.number_of_mutated_variants --- %s seconds ---" % (time.time() - start_time))
        return result

    @lru_cache()
    def number_of_mutated_variants_by_month(self, mutation, date="ALL"):
        # start_time = time.time()
        if date == "ALL":
            db = sqlite3.connect(Path("samples_data.sqlite"))
            result = db.execute(
                f"""SELECT COUNT(*) FROM data_about_mutations
                                WHERE Mutation = \"{mutation}\";
                """
            )
            result = int(list(result)[0][0])
            db.close()
        else:
            format = "%Y-%m-%d"
            first_date = datetime.strptime(date, "%Y-%m")
            last_date = last_day_of_month(first_date)
            first_date = datetime.strftime(first_date, format)
            last_date = datetime.strftime(last_date, format)
            result = self.number_of_mutated_variants(
                mutation, "ALL", first_date, last_date
            )
        # print("db.number_of_mutated_variants_by_month --- %s seconds ---" % (time.time() - start_time))
        return result

    @property
    @lru_cache()
    def mutations_names(self):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(f"SELECT mutation_name FROM mutations").fetchall()
        mutations_names = []
        for region in result:
            mutations_names.append(region[0])
        db.close()
        return mutations_names

    @lru_cache()
    def info_about_mutation(self, mutation, lang):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(
            f"""SELECT {lang}_header, {lang}_info FROM mutations
                WHERE mutation_name = \"{mutation}\"
        """
        ).fetchall()
        db.close()
        return [result[0][0], result[0][1]]

    @property
    @lru_cache()
    def text_names(self):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(f"SELECT text_name FROM information_text").fetchall()
        text_names = []
        for text in result:
            text_names.append(text[0])
        db.close()
        return text_names

    @lru_cache()
    def get_text(self, lang, text_name, table_name="information_text"):
        # start_time = time.time()
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(
            f"""SELECT text_body_{lang} FROM {table_name}
                WHERE text_name = \"{text_name}\"
        """
        ).fetchall()
        db.close()
        result = list(result)[0][0]
        # print("db.text --- %s seconds ---" % (time.time() - start_time))
        return result

    @lru_cache()
    def most_prevaling_lineages(self, region):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        result = db.execute(
            f"""SELECT most_prevaling_lineages FROM regions
                WHERE (RU_names = \"{region}\"
                OR EN_names = \"{region}\");
        """
        ).fetchall()
        most_prevaling_lineages = {}
        if result[0][0] != None:
            for lineage in result[0][0].split(";"):
                if lineage != "":
                    lineage = lineage.split(":")
                    lineage_name = lineage[0]
                    lineage_freq = lineage[1]
                    most_prevaling_lineages[lineage_name] = lineage_freq
            db.close()
        return most_prevaling_lineages

    def add_mutation_info(self, mutation, info, lang):
        db = sqlite3.connect(Path("samples_data.sqlite"))
        db.execute(
            f"""UPDATE mutations
                    SET {lang}_info = {info}
                    WHERE mutation_name = {mutation};
            """
        )
        db.commit()
        db.close()
        return
