from pathlib import Path
import sqlite3
import pandas as pd
from map_data import coordinates


def translate_regions_names(region_name):
    for regions_names in regions_dictionary:
        if region_name == regions_names[0]:
            return regions_names[1]
        elif region_name == regions_names[1]:
            return regions_names[0]


def parse_data(
    regions, adress=Path("Data", "RussianSamples.Mutations.UpTo28thFeb.txt")
):
    main_data = open(adress, "r", encoding="utf-8")
    data = pd.read_csv(main_data, sep="\t", header=None)

    mutations_names = []
    for mutations in data[3]:
        for mutation_name in mutations.split(","):
            if mutation_name not in mutations_names and mutation_name != "":
                mutations_names.append(mutation_name)
    mutations_names.sort()
    data = data.rename(
        columns={0: "sample name", 1: "date", 2: "Location_EN", 3: "mutations"}
    )
    data["Location_RU"] = data["Location_EN"]
    for region in regions:
        data["Location_RU"] = data["Location_RU"].replace(
            [region], translate_regions_names(region)
        )

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    mutation_data = pd.DataFrame(
        {}, columns=["Mutation", "Location_RU", "Location_EN", "Date", "Sample_ID"]
    )
    pandas_index = 0

    for index, row in data.iterrows():
        location = row["Location_EN"]
        date = row["date"]
        for mutation in row["mutations"].split(",")[:-1]:
            if mutation != " ":

                mutation_data.loc[pandas_index] = [
                    mutation,
                    translate_regions_names(location),
                    location,
                    date,
                    index,
                ]
                pandas_index += 1

    dbase = sqlite3.connect("samples_data.db")
    mutation_data.to_sql("data_about_mutations", dbase, if_exists="replace")
    data.to_sql("samples_data", dbase, if_exists="replace")
    dbase.execute("""DROP TABLE IF EXISTS 'mutations';""")
    dbase.execute(
        """CREATE TABLE mutations (
	                 mutation_name TEXT,
                     RU_header TEXT,
                     EN_header TEXT,
                     RU_info TEXT,
                     EN_info TEXT
	                 );"""
    )

    dbase.execute(
        f"""INSERT INTO mutations
                 (mutation_name, RU_header, EN_header, RU_info, EN_info)
                 VALUES
                 (\"ALL\",
                  \"Количество образцов в каждом регионе:\",
                  \"Number of samples in each region:\",
                  \"Размер синего круга логарифмически зависит от количества образцов, полученных из данного региона.\",
                  \"Size of the blue circle logarithmically depends on number of samples, recieved from this region.\");
                  """
    )

    for mutation in mutations_names:
        dbase.execute(
            f"""INSERT INTO mutations
                         (mutation_name, RU_header, EN_header, RU_info, EN_info)
                         VALUES
                         (\"{mutation}\",
                          \"Информация о мутации {mutation}:\",
                          \"Info about mutation {mutation}:\",
                          \"Информация об этой мутации отсутвует.\",
                          \"There is no information about this mutation.\");
                          """
        )
    dbase.commit()
    dbase.close()
    return mutations_names


def parse_regions(adress=Path("Data", "RegionsInGADM.txt")):
    regions_dict = open(adress, "r", encoding="utf-8")
    regions_dictionary = regions_dict.read().split("\n")
    for index in range(len(regions_dictionary)):
        regions_dictionary[index] = regions_dictionary[index].split(",")
    regions_dictionary.pop()

    regions = []
    for regions_names in regions_dictionary:
        regions.append(regions_names[0])

    length = len(regions)
    region_index = 0
    while region_index < length:
        # print(region_index, regions[region_index])
        if regions[region_index] in blocked:
            regions.pop(region_index)
            length -= 1
        else:
            region_index += 1

    dbase = sqlite3.connect("samples_data.db")
    dbase.execute("""DROP TABLE IF EXISTS 'regions';""")
    dbase.execute(
        """CREATE TABLE regions (
	                 RU_names TEXT,
	                 EN_names TEXT,
                     X_coordinate INTEGER,
                     Y_coordinate INTEGER
	                 );"""
    )

    for region in regions_dictionary:
        if region[0] not in blocked:
            x = coordinates[region[0]][0]
            y = coordinates[region[0]][1]
            dbase.execute(
                f"""INSERT INTO regions
                            (RU_names, EN_names, X_coordinate, Y_coordinate)
                            VALUES
                        	(\"{region[1]}\", \"{region[0]}\", {x}, {y});
                                """
            )
    dbase.commit()
    dbase.close()
    return regions, regions_dictionary


blocked = [
    "г. Севастополь",
    "Республика Крым",
    "Московская область",
    "Moskva",
    "Crimea",
    "Sevastopol'",
]
regions, regions_dictionary = parse_regions()
mutations_names = parse_data(regions)
file_for_regions = open(Path("Data", "regions.txt"), "w", encoding="utf-8")
file_for_mutations_names = open(
    Path("Data", "mutations_names.txt"), "w", encoding="utf-8"
)

for region_index in range(len(regions)):
    if region_index != len(regions) - 1:
        print(f"{regions[region_index]}", file=file_for_regions, end=",")
    else:
        print(f"{regions[region_index]}", file=file_for_regions, end="")

for mutation_name_index in range(len(mutations_names)):
    if mutation_name_index != len(mutations_names) - 1:
        print(
            f"{mutations_names[mutation_name_index]}",
            file=file_for_mutations_names,
            end=",",
        )
    else:
        print(
            f"{mutations_names[mutation_name_index]}",
            file=file_for_mutations_names,
            end="",
        )
