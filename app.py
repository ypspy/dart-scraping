# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 18:38:02 2022

@author: yoonseok
"""

from Dart_Scraper import Dart_Scraper
from os import chdir
import time
from urllib.error import URLError
from requests import exceptions
import ssl


def app(i, query):
    try:
        while True:
            print("Current page: ", i)
            
            result = Dart_Scraper(query['reportType'],
                                  i,
                                  query["start"],
                                  query["end"]
                                  )
            i += 1
            if result < 15:  # 해당 페이지 조회수가 15 미만인 경우 마지막 Page
                break
    except (FileNotFoundError,
            URLError,
            ConnectionResetError,
            ConnectionAbortedError,
            ssl.SSLEOFError,
            exceptions.SSLError) as e: 
            # 네트워크 연결 문제
        
        print("Wait for 300 seconds. Error occurred: ", e)
        
        time.sleep(300)
        app(i, query)  # 재귀 호출. 에러 발생후 발생 페이지에서 다시 시작 


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
