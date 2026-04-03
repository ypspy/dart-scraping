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
count = 0

for file in path_list_out:

    with open(file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "lxml")

    soup = str(soup).split("주석</A>")[0]
    soup = soup.replace("\n", '')
    soup = BeautifulSoup(soup, "lxml")

    # 단위 추출
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

    # IS 찾기

    for table in soup.find_all("table"):
        matches_neg = ["미처분", "미처리", "이익잉여금"]
        i = "".join(table.text.split())
        if "당기순" in i and all(x not in i for x in matches_neg):
            break
        table = BeautifulSoup("<table></table>", features="lxml").table

    matrix = matrix_generator(table)

    # Net Income Parsing

    result_string = ''
    is_line = ''

    if len(matrix) > 0:  # IS가 있을 때

        exit_key = False
        for i in matrix:
           for j in i:

               matches_neg = ["계속", "중단", "귀속", "미처분", "미처리", "처분전",
                              "지배", "비지배", "관계", "공동", "차감전", "이익잉여금"]
               j = "".join(j.split())

               if "당기순" in j and all(x not in j for x in matches_neg):

                    if len(i) == 2:  # 오리온 (2018.12)
                        is_line = [i[0], unit, i[1].replace("=", "")]
                    elif len(i) % 2 == 1:  # 주석 Column이 없을 때
                        if i[1]:
                            is_line = [i[0], unit, i[1].replace("=", "")]
                        elif i[2]:
                            is_line = [i[0], unit, i[2].replace("=", "")]
                    else:  # 주석 Column이 있을 때
                        if i[2]:
                            is_line = [i[0], unit, i[2].replace("=", "")]
                        elif i[3]:
                            is_line = [i[0], unit, i[3].replace("=", "")]

                    result_string = "_".join(is_line)
                    exit_key = True
                    break

           if exit_key == True:
               break

    elif len(matrix) == 0:  # BS가 없을 때
        result_string = ""

    result.append(result_string)
    count += 1
    print(count, end='  ')

df["netIncome"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data14.output.csv"), sep="\t")
