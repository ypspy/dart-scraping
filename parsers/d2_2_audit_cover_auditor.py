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
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]

# path collection
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*감사보고서_감사보고서*.*")

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
count = 0

for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    # 분석
    firmName = ''

    for i in soup.find_all('p'):
        pText = ''.join(i.text.split())
        if "회계법인" in pText:
            firmName = pText
        if "감사반" in pText:
            firmName = pText

    for i in soup.find_all('td'):
        pText = ''.join(i.text.split())
        if "회계법인" in pText:
            firmName = pText
        if "감사반" in pText:
            firmName = pText

    result.append(firmName)
    count += 1
    print(count, end='\n')

df["auditReportFirmName"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp001_data_001_output.csv"), sep="\t")
