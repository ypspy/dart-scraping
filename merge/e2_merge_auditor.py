# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from parsers.common import load_config

config = load_config()
OUTPUT_DIR = config["paths"]["output_dir"]

# 표지 감사인
df1 = pd.read_csv(os.path.join(OUTPUT_DIR, 'wp01.data01.output.csv'), sep="\t")
df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]  # 제거

# 보고서 감사인
df2 = pd.read_csv(os.path.join(OUTPUT_DIR, 'wp01.data05.output.csv'), sep="\t")
df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]  # 제거

# 보고서 의견
df3 = pd.read_csv(os.path.join(OUTPUT_DIR, 'wp01.data08.output.csv'), sep="\t")
df3 = df3.loc[:, ~df3.columns.str.contains('^Unnamed')]  # 제거

# 입수 정보 Key로 병합(merge) - 타임 누락 3건 공백 나타나게 조정
df = pd.merge(df1, df2[["key", "auditReportAuditor"]], on="key")
df = pd.merge(df, df3[["key", "opinion"]], how="left", on="key")

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data.auditor.csv"), sep="\t")
