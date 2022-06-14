# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 18:38:02 2022

@author: yoonseok
"""

from Dart_Scraper import Dart_Scraper
from os import chdir
import time


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
    except:
        print("Error occurred. Wait for 300 seconds.")
        
        time.sleep(300)
        app(i, query)  # 재귀 호출. 에러 발생후 발생 페이지에서 다시 시작 


# Working Directory
chdir(r"C:\results")

# Query 입력
query = {
    'reportType' : 'A001',
    'start' : 20200101,
    'end' : 20201231,
    }

# Page 1에서 Loop 시작
i = 1

# 시작
app(i, query)
