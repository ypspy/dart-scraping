# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
    matrix_generator,
)

config = load_config()
GOVERNANCE_DIR = config["paths"]["governance_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


# path collection
path_list = build_path_list(GOVERNANCE_DIR, REPORT_DIRS, "*외부감사실시내용*.*")

# year filter
path_list = (
    [x for x in path_list if "(2014." in x]
    + [x for x in path_list if "(2015." in x]
    + [x for x in path_list if "(2016." in x]
    + [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

# preprocess
df = preprocess_df(path_list)

df = df.drop([0, 1, 14, "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

path_list_out = df["path"].tolist()
df = df.drop("path", axis=1)

result = []
count = 0

for file in path_list_out:

    with open(file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "lxml")

    ptag = soup.find_all("p", string="3. 주요 감사실시내용")
    for sibling in ptag[0].next_siblings:
        if sibling.name == "table":
            table = sibling
            break

    matrix = matrix_generator(table)

    string = file + "_" + matrix[1][0] + "_" + matrix[1][2] + "_" + matrix[1][7] + "___" + matrix[2][2]
    string = string.replace("\n", " ")

    result.append(string)

    i = 5
    while matrix[i][0] != "재고자산실사(입회)":
        string = file + "_" + matrix[i][0] + "_" + matrix[i][1] + "_" + matrix[i][2] + "_" + matrix[i][4] + "_" + matrix[i][6] + "_" + matrix[i][8] + "\n"
        string = string.replace("\n", " ")

        result.append(string)

        i += 1

    count += 1
    print(count, end='  ')

df_activity = pd.DataFrame([x.split("_") for x in result])

os.makedirs(OUTPUT_DIR, exist_ok=True)
df_activity.to_csv(os.path.join(OUTPUT_DIR, "wp01.data10.output.csv"), sep="\t")
