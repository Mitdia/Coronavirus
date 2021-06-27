def create_link_to_outbreak_info(mutation):
    mutation_array = mutation.split(":")
    if mutation_array[0] == "lineage":
        return f"https://outbreak.info/situation-reports?pango={mutation_array[1]}"
    return f"https://outbreak.info/situation-reports?muts={mutation}"


def get_template_variables(db, mutation, language,  min_date, max_date):
    lang_sw = "EN"
    mutations_names = db.mutations_names[1:]
    if mutation not in mutations_names:
        mutation = "ALL"
    if language != "RU":
        print("hey!", language)
        language = "EN"
        lang_sw = "RU"
    mutation_info = db.info_about_mutation(mutation, language)
    mutation_info_header = mutation_info[0]
    mutation_info = mutation_info[1]
    text_names = db.text_names
    outbreak_info_link = create_link_to_outbreak_info(mutation)
    template_variables = {
        "outbreak_info_link": outbreak_info_link,
        "mutation": mutation,
        "mutation_info_header": mutation_info_header,
        "mutation_info": mutation_info,
        "lang": language,
        "lang_sw": lang_sw,
        "mutations_names": mutations_names,
        "min_date": min_date,
        "max_date": max_date,
    }
    for text in text_names:
        var_name = text + "_text"
        text_value = db.get_text(language, text)
        template_variables[var_name] = text_value
    return template_variables
