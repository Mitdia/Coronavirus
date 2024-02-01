from pathlib import Path
import sqlite3
import pandas as pd
from map_data import coordinates
from tqdm import tqdm


def number_of_mutated_variants(db, mutation, region):
    if region == "ALL":
        result = db.execute(
            f"SELECT COUNT(*) FROM data_about_mutations WHERE Mutation = \"{mutation}\";")
    else:
        result = db.execute(
            f"""SELECT COUNT(*) FROM data_about_mutations
                            WHERE Mutation = \"{mutation}\"
                            AND Location_EN = \"{region}\";
        """
        )
    result = int(list(result)[0][0])

    return result


def number_of_samples(db, region):
    db = sqlite3.connect(Path("flask", "samples_data.sqlite"))
    if region == "ALL":
        result = db.execute(f"SELECT COUNT(*) FROM samples_data")
    else:
        result = db.execute(f"SELECT COUNT(*) FROM samples_data WHERE Location_EN = \"{region}\";")
    result = int(list(result)[0][0])
    return result


def translate_regions_names(region_name):
    for regions_names in regions_dictionary:
        if region_name == regions_names[0]:
            return regions_names[1]
        elif region_name == regions_names[1]:
            return regions_names[0]


def get_mutations_names(data, dbase):
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
            try:
                mutation_name[2] = mutation_name[1][0]
            except IndexError:
                print(mutation_name)

            mutation_name[1] = number

            if mutation_name not in mutations_names and mutation_name != "":
                mutations_names.append(mutation_name)
    mutations_names.sort()
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
    lineages = []
    for mutation in mutations_names:

        mutation = mutation[4]
        if mutation.split(":")[0] == "lineage":
            lineages.append(mutation)
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
    print("mutations parsed!")
    dbase.commit()
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

    dbase = sqlite3.connect(Path("flask", "samples_data.sqlite"))
    dbase.execute("""DROP TABLE IF EXISTS 'regions';""")
    dbase.execute(
        """CREATE TABLE regions (
	                 RU_names TEXT,
	                 EN_names TEXT,
                     X_coordinate INTEGER,
                     Y_coordinate INTEGER,
                     most_prevaling_lineages Text
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


def get_lineage(mutations):
    mutations = mutations.split(",")
    for mutation in mutations:
        if mutation.split(":")[0] == "lineage":
            return mutation
    return "lineage:undefined"


def parse_data(regions, adress=Path("Data", "Data.csv")):
    main_data = open(adress, "r", encoding="cp1252")
    data = pd.read_csv(main_data, sep="\t", header=None)
    dbase = sqlite3.connect(Path("flask", "samples_data.sqlite"))

    mutations_names = get_mutations_names(data, dbase)

    data = data.rename(
        columns={0: "sample name", 1: "Location_EN", 2: "date", 3: "mutations"}
    )
    data["Location_RU"] = data["Location_EN"].apply(translate_regions_names)
    data["lineage"] = data["mutations"].apply(get_lineage)


    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    mutation_data = pd.DataFrame(
        {}, columns=["Mutation", "Location_RU", "Location_EN", "Date", "Sample_ID"]
    )


    pandas_index = 0
    previous_index = -1
    mutation_records_array = []
    for index, row in tqdm(data.iterrows()):
        # if index >= previous_index + 100:
        #     print(index)
        #     previous_index = index
        location = row["Location_EN"]
        date = row["date"]
        for mutation in row["mutations"].split(","):
            if mutation != " ":
                mutation_records_array.append([
                mutation,
                translate_regions_names(location),
                location,
                date,
                index,
                ])
                pandas_index += 1

    mutation_data = pd.DataFrame(mutation_records_array, columns=mutation_data.columns)
    mutation_data.to_sql("data_about_mutations", dbase, if_exists="replace")

    data.to_sql("samples_data", dbase, if_exists="replace")
    dbase.commit()
    dbase.close()


def lineages_freq(lineages_names, regions):
        dbase = sqlite3.connect(Path("flask", "samples_data.sqlite"))
        for region in regions:
            overall_number_of_samples = number_of_samples(dbase, region)
            if overall_number_of_samples == 0:
                continue
            lineages = {}
            for lineage in lineages_names:
                freq = number_of_mutated_variants(dbase, lineage, region)
                if len(lineages) < 4:
                    if freq != 0:
                        lineages[lineage] = freq
                    continue
                min_freq = min(lineages, key=lineages.get)
                if lineages[min_freq] < freq:
                    del lineages[min_freq]
                    lineages[lineage] = freq
            lineage_string = ""
            for lineage in lineages:
                lineage_string += lineage.split(":")[1] + ':' + str(round(lineages[lineage], 1)) + ';'


            dbase.execute(
                f"""UPDATE regions
                    SET most_prevaling_lineages = \"{lineage_string}\"
                    WHERE EN_names = \"{region}\";
            """
            )
            print(region)
        dbase.commit()
        dbase.close()

blocked = [
    "Московская область",
    "Moskva",
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
parse_data(regions)
