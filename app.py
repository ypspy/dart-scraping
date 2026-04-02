# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 18:38:02 2022

@author: yoonseok
"""

from scraper.dart_scraper import dart_scraper
from os import chdir
import time
from urllib.error import URLError
from requests import exceptions
import ssl
import yaml
from pathlib import Path
config_path = Path(__file__).parent / "config.yaml"
with open(config_path, encoding="utf-8") as f:
    config = yaml.safe_load(f)


def app(i, query):
    while True:
        try:
            while True:
                print("Current page: ", i)

                result = dart_scraper(query['reportType'],
                                      i,
                                      query["start"],
                                      query["end"]
                                      )
                i += 1
                if result < 15:  # 해당 페이지 조회수가 15 미만인 경우 마지막 Page
                    break
            break  # success, exit retry loop
        except (FileNotFoundError,
                URLError,
                ConnectionResetError,
                ConnectionAbortedError,
                ssl.SSLEOFError,
                exceptions.SSLError) as e:
                # 네트워크 연결 문제

            print("Wait for 300 seconds. Error occurred: ", e)

            time.sleep(config["scraper"]["delay_seconds"])
            continue


# Working Directory
chdir(input("Enter location (C:\F001_2020): "))

# Query 입력
query = {
    'reportType' : str(input("Enter reportType (A001, F001): ")),
    'start' : input("Registered from (20200101): "),
    'end' : input("Registered to (20201231): "),
    }

# Page 1에서 Loop 시작 #1708)
i = int(input("loop start(resume) from page Number: "))

# 시작
app(i, query)
