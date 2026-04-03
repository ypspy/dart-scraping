# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
)

config = load_config()
GOVERNANCE_DIR = config["paths"]["governance_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


# path collection
path_list = build_path_list(GOVERNANCE_DIR, REPORT_DIRS, "*외부감사실시내용*.*")

# year filter (외부감사실시내용 "4. 감사(감사위원회)와의 커뮤니케이션"는 2019년부터 포함)
path_list = [x for x in path_list if "(2019." in x]

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

    ptag = soup.find_all("p", string="4. 감사(감사위원회)와의 커뮤니케이션")  # 서식에서 수정불가능한 요소임
    for sibling in ptag[0].next_siblings:
        if sibling.name == "table":
            table = sibling
            break

    result_string = ''

    if ''.join(table.text.split()).find("감사위원회") > 0:
        result_string = "감사위원회"

    result.append(result_string)
    count += 1
    print(count, sep="  ")

df["AC1"] = result

df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data19.output.csv"), sep="\t")
