# -*- coding: utf-8 -*-
"""
Refactoring (2022. 06)
1. DART에서 OpenAPI를 제공한 이후 직접 접근하는 것이 더 제한되어 있음. 변경된 환경 반영하여 수정 작업 필요
2. Parsing 프로세스 : 입수 문서의 수 AxBxC
    공시 문서의 주소를 입수 (A)
    → 공시 문서에서 첨부 문서 주소 입수 (B) 
    → 첨부 문서에서 하위 문서 HTML 주소 입수 (C) ▶ HTML 입수
3. Unique Key 생성 문제 : 고유번호_접수번호_문서명_사업연도종료일
"""

import requests 
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import js2py
import urllib.request


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
    DocListSoup = BeautifulSoup(companyList.content, "html.parser")
    
    corpList = DocListSoup.findAll("td")
    loop = 1  # 최대 15개의 주소를 loop한다. 주소당 td 태그가 6개. corpList는 Max 90.
    docList = {}  # 고유번호와 문서 주소를 dictionary에 담는다.

    while True:
        docAddress = "http://dart.fss.or.kr" + corpList[loop+1].a["href"]  # db 접근용 주소
        doc_key = '_'.join([reportType,
                            corpList[loop].a["href"][28:36],
                            docAddress.split('=')[1]
                            ])  # 문서 고유번호 생성    
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
    docSoup = BeautifulSoup(docHTML.content, "html.parser")    
    
    # 문서와 첨부 문서의 URL 주소 추출
    subDocList = docSoup.findAll("option")
    subDocAddressList = []
    loop = 1
    while True:
        subDocAddress = "http://dart.fss.or.kr/dsaf001/main.do?" + subDocList[loop]["value"]
        if subDocAddress != 'http://dart.fss.or.kr/dsaf001/main.do?null':  # 옵션 값이 null인 경우 제
            subDocAddressList.append(subDocAddress)     
        loop += 1
        if loop > len(subDocList)-1:
            break

    subDocAddressList = list(set(subDocAddressList))  # 중복제거
    
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
    
    addList = []
    for i in dictList:
        for j in ["id", "tocNo", "text"]:
            i.pop(j, None)
        
        address = "http://dart.fss.or.kr/report/viewer.do?" + urlencode(i)
        addList.append(address)

    return addList

# 리포트타입 결정
reportType = "A001"

# 보고서 주소 추출
docAddressDict = Document_Address_Parser(1, 20210531, 20220531, reportType)
docAddress = list(docAddressDict.items())[0][1]  # temporary

# 보고서 내부 개별 문서 주소 추출
subDocAddressList = SubDocument_Address_Parser(docAddress)
subDocAddress = subDocAddressList[0]

# 개별 문서 내부 HTML 주소 추출
htmlAddress = HTML_Address_Parser(subDocAddress)

# Html로 저장
urllib.request.urlretrieve(htmlAddress[10],
                           r"C:\Users\yoont\test.html")
