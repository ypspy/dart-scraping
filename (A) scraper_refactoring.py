# -*- coding: utf-8 -*-
"""
Refactoring (2022. 06)
1. DART에서 OpenAPI를 제공한 이후 직접 접근하는 것이 더 제한되어 있음. 변경된 환경 반영하여 수정 작업 필요
"""

import requests 
from urllib.parse import urlencode
from bs4 import BeautifulSoup


def Address_Parser(i, startDate, endDate, reportType):
    """    
    Parameters
    ----------
    i : int
        전체 페이지 중 현재 진행중인 페이지 번호
    startDate : int
        대상기간 시작일. yyyymmdd 포멧으로 입력 사업보고서/감사보고서는 1999년 3월부터 공시내역이 존재
    endDate : int
        대상기간 종료일. yyyymmdd 포멧. 공시일이므로, 회계기간 종료일과 혼동하지 말 것
    reportType : str
        상세유형 (출처: DART 오픈API 개발가이드)
        A001 사업보고서    A002 반기보고서   A003 분기보고서
        F001 감사보고서    F002 연결감사보고서 F003 결합감사보고서    F004 회계법인사업보고서

    Returns
    -------
    Soup
        BeautifulSoup 라이브러리로 생성한 수프가 반환됨

    """
   
    detailSearch = "http://dart.fss.or.kr/dsab007/detailSearch.ax?"
    # DART 사이트 개편으로 detail Search DB 경로가 변경되었음
    data = {  
              'currentPage': i,
              'maxResults': 15,
              'maxLinks': 10,
              'startDate': startDate,
              'endDate': endDate,
              'finalReport': 'recent',
              'publicType': reportType,         
           }
    query_string = urlencode(data)
    listURL = detailSearch + query_string 
    companyList = requests.get(listURL)  
    # DART는 Post로 요청하나 requests로 post하면 안됨. query string 만들어서 get으로 요청함
    
    return BeautifulSoup(companyList.content, "html.parser")

soup = Address_Parser(1, 20210531, 20220531, "A001")
