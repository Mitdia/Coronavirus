from datetime import datetime
from functools import lru_cache


@lru_cache()
def check_date_format(date_string):
    if date_string == None:
        return False
    format = "%Y-%m-%d"
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


@lru_cache()
def check_mutation_format(db, mutation):
    mutations_names = db.mutations_names
    if mutation not in mutations_names:
        print("Fail!")
        return False
    return True


@lru_cache()
def check_language_format(lang):
    if lang not in ["EN", "RU"]:
        print("Fail!")
        return False
    return True


@lru_cache()
def security_check(db, mutation, lang, min_date, max_date):
    if (
        not check_mutation_format(db, mutation)
        or not check_language_format(lang)
        or not check_date_format(min_date)
        or not check_date_format(max_date)
    ):
        return False
    return True
