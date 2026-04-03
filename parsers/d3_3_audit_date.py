# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import re
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
)

config = load_config()
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]

# path collection
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*감사인의감사보고서*.*")

# year filter
path_list = (
    [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

# preprocess
df = preprocess_df(path_list)
path_list_out = df["path"].tolist()

p = re.compile("[0-9]{4}년[0-9]{1,2}월[0-9]{1,2}일")
count = 0
result = []

for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    # 분석
    content = ''.join(soup.text.split())
    firstPart = content.split("의견근거")[0]
    secondPart = content.split("재무제표에대한경")
    secondPart = secondPart[len(secondPart) - 1]
    content = firstPart + secondPart

    output = set(p.findall(content))

    resultString = ''

    for i in output:
        resultString = resultString + i + "_"

    result.append(resultString)
    count += 1
    print(count, end='\n')

df["auditReportDate"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data04.output.csv"), sep="\t")
