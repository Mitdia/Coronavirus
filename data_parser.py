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


def parse_data(regions, adress=Path("Data", "RussianSamples.GISAID.20210622.csv")):
    main_data = open(adress, "r", encoding="utf-8")
    data = pd.read_csv(main_data, sep="\t", header=None)
    dbase = sqlite3.connect("samples_data.sqlite")

    mutations_names = []
    for mutations in data[3]:
        for mutation_name_raw in mutations.split(","):
            if mutation_name_raw == "":
                continue
            mutation_name = [0, 0, "", "", ""]
            mutation_name[4] = mutation_name_raw
            mutation_name[0], mutation_name[1] = mutation_name_raw.split(":")
            mutation_name[0] = genes.index(mutation_name[0])

            rodata = mutation_name[1][1:]
            number = 0
            count = 1
            for i in range(len(rodata)):
                num = rodata[i]
                if num in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    number *= 10
                    number += ord(num) - ord("0")
                    count += 1
                else:
                    break
            mutation_name[3] = mutation_name[1][count:]
            mutation_name[2] = mutation_name[1][0]
            mutation_name[1] = number

            if mutation_name not in mutations_names and mutation_name != "":
                mutations_names.append(mutation_name)
    mutations_names.sort()
    data = data.rename(
        columns={0: "sample name", 1: "Location_EN", 2: "date", 3: "mutations"}
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

        mutation = mutation[4]
        print(mutation, end=" ")
        dbase.execute(
            f"""INSERT INTO mutations
                         (mutation_name, RU_header, EN_header, RU_info, EN_info)
                         VALUES
                         (\"{mutation}\",
                          \"Распространенность {mutation}:\",
                          \"Distribution of {mutation}:\",
                          \"Информация об этой мутации отсутвует.\",
                          \"There is no information about this mutation.\");
                          """
        )

    dbase.commit()

    pandas_index = 0
    previous_index = -1

    for index, row in data.iterrows():
        if index >= previous_index + 100:
            print(index)
            previous_index = index
        location = row["Location_EN"]
        date = row["date"]
        for mutation in row["mutations"].split(","):
            if mutation != " ":

                mutation_data.loc[pandas_index] = [
                    mutation,
                    translate_regions_names(location),
                    location,
                    date,
                    index,
                ]
                pandas_index += 1

    mutation_data.to_sql("data_about_mutations", dbase, if_exists="replace")
    data.to_sql("samples_data", dbase, if_exists="replace")
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

    dbase = sqlite3.connect("samples_data.sqlite")
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

genes = [
    "lineage",
    "leader",
    "nsp2",
    "nsp3",
    "nsp4",
    "3C",
    "nsp6",
    "nsp7",
    "nsp8",
    "nsp9",
    "nsp10",
    "RdRp",
    "helicase",
    "exonuclease",
    "endornase",
    "methyltransferase",
    "nsp11",
    "ORF1a",
    "ORF1b",
    "S",
    "ORF3a",
    "E",
    "M",
    "ORF6",
    "ORF7a",
    "ORF7b",
    "ORF8",
    "N",
    "ORF10",
]
regions, regions_dictionary = parse_regions()
mutations_names = parse_data(regions)
file_for_regions = open(Path("Data", "regions.txt"), "w", encoding="utf-8")
file_for_mutations_names = open(
    Path("Data", "mutations_names.txt"), "w", encoding="utf-8"
)
