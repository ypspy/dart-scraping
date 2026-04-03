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

result = []
count = 0

KGAAP = ["일반기업회계기준에따라", "일반회계기준에따라", "一般企業會計基準에따라", "일반기업회계처리기준에따라",
         "'일반기업회계기준'에 따라"]
KIFRS = ["한국채택국제회계기준에따라", "한국채택회계기준"]
OTHERS = ["공기업ㆍ준정부기관회계사무규칙에따라", "지방공기업법및지방공기업결산지침에따라",
          "지방공기업법(령)및지방공기업결산지침에따라", "일반기업회계기준및",
          "지방공기업법과행정자치부의지방공기업결산지침,대구도시공사정관및회계규정에따라"]

GAAP = [KGAAP, KIFRS, OTHERS]
tag = ["일반기업회계기준", "한국채택국제회계기준", "기타기준"]


# disclaimer of opinion
keyWord1 = ['의견거절근거', '의견을표명하지않', '감사의견을표명하지아니합니다', '의견을표명하지아니', '의견을표명할수없']
# qualified
keyWord2 = ['한정의견근거', '한정의견근거단락에기술된사항이미치는영향을제외']
# adverse
keyWord3 = ['부적정의견근거', '부적정의견근거단락에서기술된사항의유의성']

keyWord = [keyWord1, keyWord2, keyWord3]
opinion = ["의견거절", "한정", "부적정"]


for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    content = ''.join(soup.text.split())

    num = 0

    accountingStandard = "예외"
    for i in GAAP:
        for j in i:
            if j in content:
                accountingStandard = tag[num]
                break
        num += 1

    num = 0

    auditOpinion = "적정"
    for i in keyWord:
        for j in i:
            if j in content:
                auditOpinion = opinion[num]
                break
        num += 1
    returnText = accountingStandard + "\t" + auditOpinion

    result.append(returnText)

    count += 1
    print(count, end='  ')

df["GAAP"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data13_output.csv"), sep="\t")
