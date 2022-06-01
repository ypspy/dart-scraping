# -*- coding: utf-8 -*-
"""
Created on Mon May 17 23:40:48 2021

@author: yoonseok
"""

import os
import pandas as pd

os.chdir(r"C:\Users\yoont\Desktop\output\\")

# 외부감사 실시내용 총시간 정보 (MultiHeader 조정 필요)
df1 = pd.read_excel('wp01.data.time.xlsx', sheet_name='data')

# 상장여부 STOCK 
df2 = pd.read_excel('wp01.data.period.xlsx', sheet_name='data')
df2 = df2[df2["drop"] != 1]
del df2['drop']

# 감사인 FIRST AUDCHA OPINION TYPE 
df3 = pd.read_excel('wp01.data.auditor.xlsx', sheet_name='data')

# 감사보고서일 LAG
df4 = pd.read_excel('wp01.data.reportdate.xlsx', sheet_name='data')
df4 = df4[df4["drop"] != 1]
del df4['drop']

# 재무제표 작성기준 IFRS 
df5 = pd.read_excel('wp01.data.gaap.xlsx', sheet_name='data')

# 재무정보 SIZE LEV ROA LOSS INVREC
df6 = pd.read_excel('wp01.data.financials.xlsx', sheet_name='data')
df6 = df6[df6["drop"] != 1]
del df6['drop']

# 재무제표 작성기준 MAT IC
df7 = pd.read_excel('wp01.data.internalControl.xlsx', sheet_name='data')

# 감사위원회 설치여부 AC
df8 = pd.read_excel('wp01.data.governance.xlsx', sheet_name='data')

# 입수 후 전처리 Data 취합. Inner join한다.

df = pd.merge(df6, df2[["key", "STOCK"]], how="left", on="key")  # 재무정보 + 상장여부
df = pd.merge(df, df7[["key", "MAT", "IC"]], how="left", on="key")
df = pd.merge(df, df8[["key", "AC"]], how="left", on="key")
df = pd.merge(df, df5[["key", "IFRS"]], how="left", on="key")
df = pd.merge(df, df3[["key", "AUDCHA", "FIRST", "OPINION", "TYPE"]], how="inner", on="key")
df = pd.merge(df, df4[["key", "LAG"]], how="inner", on="key")

# 타임정보/활동정보 마지막
df = pd.merge(df, df1, how="left", on="key")

# 12월 말이 아닌 기업 제거

df = df[(df["5"] == "(2017.12)") | (df["5"] == "(2018.12)") | (df["5"] == "(2019.12)")]

# 금융업 제거

df_ind = pd.read_excel("industry.xlsx", dtype={'KSIC': str}, sheet_name='data')
df = df.rename(columns={"11": "INDUSTRY"})

df = pd.merge(df, df_ind, on = "INDUSTRY", how ='left')
df = df[df["FIN"] == 0]

# 감사시간 합계 100시간 미만 제거

df = df[df["TOTAL"] >= 100]

# Export 전 정리
df.fillna(0, inplace=True) # NA 제거

# CSV로 추출
df.to_csv("wp01.data.output.csv", sep="\t")
