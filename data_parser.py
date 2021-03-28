from pathlib import Path

import pandas as pd


def translate_regions_names_from_english_to_russian(region_name):
    for regions_names in regions_dictionary:
        if region_name == regions_names[0]:
            return regions_names[1]


def translate_regions_names_from_russian_to_english(region_name):
    for regions_names in regions_dictionary:
        if region_name == regions_names[1]:
            return regions_names[0]


def parse_data(adress=Path("Data", "RussianSamples.Mutations.UpTo28thFeb.txt")):
    main_data = open(adress, "r")
    parsed_data = pd.read_csv(main_data, sep="\t", header=None)

    mutations_names = []
    for mutations in parsed_data[3]:
        for mutation_name in mutations.split(","):
            if mutation_name not in mutations_names and mutation_name != "":
                mutations_names.append(mutation_name)
    mutations_names.sort()
    parsed_data = parsed_data.rename(
        columns={0: "sample name", 1: "date", 2: "location", 3: "mutations"}
    )

    for region_index in range(len(parsed_data["location"])):
        region = translate_regions_names_from_english_to_russian(
            parsed_data["location"][region_index]
        )
        parsed_data["location"][region_index] = region

    for mutation_index in range(len(mutations_names)):
        mutation_parsed = []
        mutation = mutations_names[mutation_index]
        for sample_mutations in parsed_data["mutations"]:
            if mutation in sample_mutations.split(","):
                mutation_parsed.append(1)
            else:
                mutation_parsed.append(0)
        parsed_data[mutation] = mutation_parsed

    return parsed_data, mutations_names


def parse_regions(adress=Path("Data", "RegionsInGADM.txt")):
    regions_dict = open(adress, "r")
    regions_dictionary = regions_dict.read().split("\n")
    for index in range(len(regions_dictionary)):
        regions_dictionary[index] = regions_dictionary[index].split(",")
    regions_dictionary.pop()

    regions = []
    for regions_names in regions_dictionary:
        region_name = regions_names[1]
        regions.append(region_name)

    length = len(regions)
    region_index = 0
    while region_index < length:
        # print(region_index, regions[region_index])
        if regions[region_index] in blocked:
            regions.pop(region_index)
            length -= 1
        else:
            region_index += 1

    return regions, regions_dictionary


blocked = ["г. Севастополь", "Республика Крым", "Московская область"]
regions, regions_dictionary = parse_regions()
data, mutations_names = parse_data()

file_for_data = open(Path("Data", "data.csv"), "w")
file_for_regions = open(Path("Data", "regions.txt"), "w")
file_for_mutations_names = open(Path("Data", "mutations_names.txt"), "w")
print(data.to_csv(index=False), file=file_for_data)

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
