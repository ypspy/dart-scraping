# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
    matrix_generator, find_target_table,
)

config = load_config()
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


def parsing_time(matrix, is_comparative, table_length, report):
    if is_comparative:
        container = []
        table_length = int(table_length / 2)
        for i in range(table_length):
            container.append(matrix[report][1] + "_" + matrix[1][2+2*i] + "_" + matrix[report][2+2*i].replace('-', '0').replace(',',''))
    else:
        container = []
        table_length = int(table_length)
        for i in range(table_length):
            container.append(matrix[report][1] + "_" + matrix[1][2+i] + "_" + matrix[report][2+i].replace('-', '0').replace(',',''))
    return container


def indexing(matrix):
    """
    당기, 전기 부분 삭제한 경우들이 있어서 찾아야함
    """
    container = []
    for i in matrix:
        try:
            i[0:2].index("투입 인원수")
            container.append(matrix.index(i))
        except ValueError:
            pass
        try:
            i[0:2].index("분ㆍ반기검토")
            container.append(matrix.index(i))
        except ValueError:
            pass
        try:
            i[0:2].index("감사")
            container.append(matrix.index(i))
        except ValueError:
            pass
        try:
            i[0:2].index("합계")
            container.append(matrix.index(i))
        except ValueError:
            pass
    return container


# path collection
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*외부감사실시내용*.*")

# year filter
path_list = (
    [x for x in path_list if "(2017." in x]
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
# df columns: 2,3,4,5,6,7,8,9,10,11,12,13,con,amend,key
# df.iloc[count, 14] == "key"

result = []
count = 0

for file in path_list_out:

    with open(file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "lxml")

    table = find_target_table(soup)

    matrix = matrix_generator(table)
    is_comparative = matrix[1][2] == matrix[1][3]
    table_length = len(matrix[1]) - 2

    container = indexing(matrix)

    for j in container:
        return_list = parsing_time(matrix, is_comparative, table_length, j)
        for k in return_list:
            result.append(df.iloc[count, 14] + "_" + k)
    count += 1
    print(str(count), end='\n')

df_time = pd.DataFrame([x.split("_") for x in result])
df_time.columns = ["key", "B", "C", "D"]

df_time = df_time.pivot_table(values="D",
                              index=["key"],
                              columns=["B", "C"],
                              aggfunc="first")

os.makedirs(OUTPUT_DIR, exist_ok=True)
df_time.to_csv(os.path.join(OUTPUT_DIR, "wp001_data_007_output.csv"), sep="\t")
