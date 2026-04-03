# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
    matrix_generator,
)

config = load_config()
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


# path collection
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*(첨부)*.*")

# year filter
path_list = (
    [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

# preprocess
df = preprocess_df(path_list)
path_list_out = df["path"].tolist()

result = []

for file in path_list_out:

    with open(file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "lxml")

    soup = str(soup).split("주석</A>")[0]
    soup = soup.replace("\n", '')
    soup = BeautifulSoup(soup, "lxml")

    # 분석
    for td in soup.find_all(["p", "td"]):
        if ''.join(td.text.split()).find("단위") > 0:
            unit = ''.join(td.text.split())
            if unit.find(":원") > 0:
                unit = '1'
            elif unit.find(":천원") > 0:
                unit = '1000'
            elif unit.find(":백만원") > 0:
                unit = '1000000'
            else:
                unit = "NA"
            break

    for table in soup.find_all("table"):
        if ''.join(table.text.split()).find("부채") > 0:
            break
        table = BeautifulSoup("<table></table>", features="lxml").table  # 의견 거절 등 BS가 안붙어있을 때 처리

    matrix = matrix_generator(table)

    # 부채와자본총계(=자산총계) Parsing

    result_string = ''
    bs_line = ''

    if len(matrix) > 0:  # BS가 있을 때
        i = matrix[len(matrix)-1]
        if len(matrix[0]) == 2:  # 오리온 (2018.12)
            bs_line = [i[0], unit, i[1].replace("=", "")]
        elif len(matrix[0]) % 2 == 1:  # 주석 Column이 없을 때
            if i[1]:
                bs_line = [i[0], unit, i[1].replace("=", "")]
            elif i[2]:
                bs_line = [i[0], unit, i[2].replace("=", "")]

        else:  # 주석 Column이 있을 때
            if i[2]:
                bs_line = [i[0], unit, i[2].replace("=", "")]
            elif i[3]:
                bs_line = [i[0], unit, i[3].replace("=", "")]

        result_string = "_".join(bs_line)
    elif len(matrix) == 0:  # BS가 없을 때
        result_string = ""

    result.append(result_string)
    print('.', end='')

df["totalAsset"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp001_data_008_output.csv"), sep="\t")
