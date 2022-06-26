# -*- coding: utf-8 -*-
"""
Refactoring (2022. 06)
1. DART에서 OpenAPI를 제공한 이후 직접 접근하는 것이 더 제한되어 있음. 변경된 환경 반영하여 수정 작업 필요
2. Parsing 프로세스 : 입수 문서의 수 AxBxC
    공시 문서의 주소를 입수 (A)
    → 공시 문서에서 첨부 문서 주소 입수 (B) 
    → 첨부 문서에서 하위 문서 HTML 주소 입수 (C) ▶ HTML 입수
3. Unique Key 생성 문제 : 고유번호_접수번호_문서명_사업연도종료일
4. scraper_refactoring에서 loop 가능하도록 Dart_Scraper로 변경 
"""

import requests 
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import js2py
import urllib.request
from os import path
import time
from tqdm import tqdm


def Document_Address_Parser(i, startDate, endDate, reportType):
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
    docList : dict
        {key, value} = {감독원 고유번호, 문서리스트 주소}

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
    time.sleep(1)  # 1분에 100개 규정 고려. Request당 1초 대기
    
    DocListSoup = BeautifulSoup(companyList.content, "html.parser")
    
    corpList = DocListSoup.findAll("td")
    loop = 1  # 최대 15개의 주소를 loop한다. 주소당 td 태그가 6개. corpList는 Max 90.
    docList = {}  # 고유번호와 문서 주소를 dictionary에 담는다.

    while True:
        docAddress = "http://dart.fss.or.kr" + corpList[loop+1].a["href"]  # db 접근용 주소
        docName = ''.join(corpList[loop+1].a.text.split())
        reportName = docName.split('(')[0]
        yearEnd = '(' + docName.split('(')[1]
        doc_key = '_'.join([reportType,
                            corpList[loop].a["href"][28:36],
                            docAddress[44:],
                            reportName,
                            yearEnd
                            ])  # key 생성
        docList[doc_key] = docAddress
        loop += 6
        if loop > len(corpList):  # 마지막 페이지 등에서 문서 수가 15개가 안되면 오류 발생함
            break
    
    return docList

def SubDocument_Address_Parser(docAddress):
    """    
    Parameters
    ----------
    docAddress : str
        추출된 문서주소 리스트 중 1건

    Returns
    -------
    subDocAddressList : List
        문서 묶음에 포함된 문서 주소 리스트 (ex. 사업보고서, 정정보고서, 감사보고서 등)

    """
    
    # 문서 최초 조회
    docHTML = requests.get(docAddress)
    time.sleep(1)  # 1분에 100개 규정 고려. Request당 1초 대기
    docSoup = BeautifulSoup(docHTML.content, "html.parser")    
    
    # 문서와 첨부 문서의 URL 주소 추출
    subDocList = docSoup.findAll("option")
    subDocAddressList = {}
    loop = 1
    while True:

        subDocAddress = "http://dart.fss.or.kr/dsaf001/main.do?" + subDocList[loop]["value"]
        if subDocAddress != 'http://dart.fss.or.kr/dsaf001/main.do?null':  # 옵션 값이 null인 경우 제
            docName = ''.join(subDocList[loop].text.split())
            
            subDocName = '_'.join([subDocAddress[44:58],
                                  '_'.join([docName[:10], docName[10:]])])# Key 생성
            subDocAddressList[subDocName] = subDocAddress
        
        loop += 1
        if loop > len(subDocList)-1:
            break
    
    return subDocAddressList

def HTML_Address_Parser(subDocAddress):
    """    
    Parameters
    ----------
    subDocAddress : str
        문서 묶음에 포함된 문서 주소

    Returns
    -------
    subDocAddressList : List
        문서 묶음에 포함된 문서 주소 리스트 (ex. 사업보고서, 정정보고서, 감사보고서 등)

    """    
    
    docHTML = requests.get(subDocAddress)    
    time.sleep(1)  # 1분에 100개 규정 고려. Request당 1초 대기
    
    docSoup = BeautifulSoup(docHTML.content, "html.parser")

    # HTML의 script tag 안애 포함된 내용을 취합
    jScripts = ''
    for i in docSoup.findAll("script"):
        jScripts += i.text

    # script tag 중 initPage() 함수에 포함된 script 추출
    jScripts = jScripts.split("winCorpInfo');")[1]
    jScripts = jScripts.split("//js tree")[0]

    # 추출된 JS code를 실행시켜 개별 문서 html 주소 정보 추출 ()
    context = js2py.EvalJs(enable_require=True)
    context.execute(jScripts)  # treeData
    
    dictList = list(context.treeData)
    
    for i in dictList: i.pop('children', None)  # 문서 소분류 제거
    
    addList = {}  # 고유번호와 문서 주소를 dictionary에 담는다.
    # addList = []
    for i in dictList:
        docName = ''.join(i["text"].split())  # key 생성
        for j in ["id", "tocNo", "text"]:
            i.pop(j, None)
        
        address = "http://dart.fss.or.kr/report/viewer.do?" + urlencode(i)
        addList[docName] = address

    return addList

def Get_HTML(htmlAddress, docKey):  # 재귀함수로 에러 부분 계속 시도
    try:
        urllib.request.urlretrieve(htmlAddress, docKey)
    except FileNotFoundError:
        print("Error Occurred at", htmlAddress)
        time.delay(3)
        Get_HTML(htmlAddress, docKey)

def Dart_Scraper(reportType,  # report type 선택 A001: 사업보고서
                 currentPage,  # 현재 page 선택
                 startDate,
                 endDate,
                 delay=1):
    # 보고서 주소 추출
    docAddressDict = Document_Address_Parser(currentPage, startDate, endDate, reportType)
    docsInThisPage = list(docAddressDict.items())

    for i in tqdm(docsInThisPage, desc="docs in this page"):
        docAddress = i[1]
        
        # 보고서 내부 개별 문서 주소 추출
        subDocAddressDict = SubDocument_Address_Parser(docAddress)
        subDocAddressList = list(subDocAddressDict.items())
        
        for subDocAddress in tqdm(subDocAddressList, desc="1st loop", leave=False):            
            # 개별 문서 내부 HTML 주소 추출
            htmlAddressDict = HTML_Address_Parser(subDocAddress[1])
            htmlAddressList = list(htmlAddressDict.items())
            
            for html in tqdm(htmlAddressList, desc="2nd loop", leave=False):                    
                docKey = '_'.join([i[0],  # 보고서 타입, FSS 고유번호, 문서접수번호, 접수문서명, 보고기간말
                                   subDocAddress[0],  # 문서접수번호 + 제출일과 본(첨부)문서명
                                   html[0],  # 문서명
                                   '.html'])  # HTML 확장자
                                
                if path.exists(docKey):
                    None  # 실행 중단 후 다시 시작하는 경우 중복으로 쓰지 않음
                else:
                    Get_HTML(html[1], docKey)  # 에러 발생하면 계속 시도. 발생지점에서 에러가 생기는 것이 아님.
                    time.sleep(delay)  # 1분에 100개 규정 고려. Request당 1초 대기
    
    return len(docsInThisPage)  # 페이지 문서수 반환 (Max: 15, 변경 가능)                
