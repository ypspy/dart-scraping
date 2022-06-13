# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 18:38:02 2022

@author: yoonseok
"""

from Dart_Scraper import Dart_Scraper
from os import chdir

chdir(r"C:\results")    

i = 2
while True:
    result = Dart_Scraper("A001", i, 20200101, 20201231, delay=1)
    i += 1
    if result < 15:  # 해당 페이지 조회수가 15 미만인 경우 마지막 Page
        break
