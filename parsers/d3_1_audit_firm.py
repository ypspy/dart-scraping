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

file = open(os.path.join(WORKING_DIR, "wp01.data02_auditor.txt"), 'r', encoding='utf-8')
import_list = file.readlines()
auditor_list = []

for i in import_list:
    auditor_list.append(i.replace("\n", ''))

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

count = 0
result = []

for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    # 분석
    content = ''.join(soup.text.split())
    dictionary = {}

    container = []
    for i in auditor_list:
        if i in content:
            loc = content.find(i)
            dictionary[i] = loc
            container.append(i)
            content = content.replace(i, '')

    if len(container) == 0:
        container.append('-')
        dictionary["None"] = '-'

    sorted_dictionary = {}
    sorted_keys = sorted(dictionary, key=dictionary.get)

    for w in sorted_keys:
        sorted_dictionary[w] = dictionary[w]

    auditFirm = list(sorted_dictionary)[-1]

    result.append(auditFirm)
    count += 1
    print(count, end='\n')

df["auditReportAuditor"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data05.output.csv"), sep="\t")
