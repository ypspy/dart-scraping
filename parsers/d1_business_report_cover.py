# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
)

config = load_config()
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


# 1. 타겟 폴더에 있는 필요 문서 경로 리스트업
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*사업보고서_사업보고서*.*")

# 2. 분리 (year filter)
path_list = (
    [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

# 3. Preprocess
df = preprocess_df(path_list)
path_list_out = df["path"].tolist()

result = []
count = 0

for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    # 분석
    container = []
    for i in soup.find_all("tr"):
        j = "".join(i.text.replace("\n", "").split())

        if j.count("부터") - j.count("면제") - j.count("제외") == 1:
            container.append(j)
        elif j.count("까지") == 1:
            container.append(j)
        elif j.count("회사명") == 1:
            container.append(j)
        elif j.count("법인유형") == 1:
            container.append(j)

    joinedString = "_".join(container)

    result.append(joinedString)
    count += 1
    print(count, end='\n')

df["businessReportCover"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data01.output.csv"), sep="\t")
