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
path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*감사보고서_내부회계관리제도*.*")

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

# 내부회계관리제도 감사보고서

# disclaimer of opinion
AkeyWord1 = ['의견을표명하지', '의견거절근거']
# adverse
AkeyWord2 = ['효과적으로설계및운영되고있지', '부적정의견근거']
# material weakness
AkeyWord3 = ['중요한취약점이언급', "중요한취약점이발견되었"]

AkeyWord = [AkeyWord1, AkeyWord2, AkeyWord3]
Aopinion = ["의견거절", "부적정", "중요한취약점"]


# 내부회계관리제도 검토보고서

# disclaimer of opinion
RkeyWord1 = ['검토의견을표명하지']
# qualified
RkeyWord2 = ['를얻을수', '절차를수', '미치는영향을']
# material weakness
RkeyWord3 = ['중요한취약점이언급', "중요한취약점이발견되었"]

RkeyWord = [RkeyWord1, RkeyWord2, RkeyWord3]
Ropinion = ["의견거절", "한정", "중요한취약점"]

count = 0

for file in path_list_out:

    with open(file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "lxml")
    report_type = ""

    content = ''.join(soup.text.split())

    if "내부회계관리제도에대한경영진과지배기구의책임" in content:
        report_type = "A"
    else:
        report_type = "R"

    num = 0
    container = []
    return_text = report_type + "_" + "적정"

    if report_type == "A":
        key_word = AkeyWord
        opinion = Aopinion
    else:
        key_word = RkeyWord
        opinion = Ropinion


    for i in key_word:
        for j in i:
            if j in content:
                return_text = report_type + "_" + opinion[num]
                break

        num += 1
    result.append(return_text)
    count += 1
    print(count, end='  ')

df["opinion"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data12_output.csv"), sep="\t")
