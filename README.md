# DART 공시파일 입수
## 개요
### 금융감독원 오픈 API
금융감독원이 설명하는 바에 따르면 DART 오픈API는 다음과 같은 목적으로 활용 가능하다. 

<blockquote>
- DART 공시원문 활용 : DART에 공시되는 공시보고서의 원문을 XML형식으로 다운로드받아 원하는 자료를 자유롭게 추출하여 사용 <br>
- 주요공시 및 재무정보 제공 : 사업보고서 주요항목 및 주요재무계정, 지분보고서 종합정보를 데이터 형식으로 바로 활용<br>
- 대용량 재무정보 제공 : 상장법인(금융업 제외)에서 제출한 전체 재무제표를 분기별로 다운로드
(https://opendart.fss.or.kr/intro/main.do)
</blockquote>    
    
오픈API는 사용 약관에 따라 개인, 기업 각각에게 서로 다른 한도를 부여한다.  

<blockquote>
1. 개인 : 일 10,000건 (서비스별 한도가 아닌 오픈API 23종 전체 서비스 기준)<br>
2. 기업(사업자등록증 및 IP 등록)<br>
1) 공시목록, 기업개황 2종 : 한도 없음(기존 DART홈페이지 오픈API와 동일)<br>
2) 공시원문, 사업보고서 주요정보 등 신규서비스 21종 : 일 10,000(서비스별 한도가 아닌 21종 서비스 전체 기준)

* 일일한도를 준수하더라도 서비스의 안정적인 운영을 위하여 과도한 네트워크 접속(분당 100회 이상)은 서비스 이용이 제한될 수 있으니 이용에 참고하시기 바랍니다.
</blockquote>

분당 100회 이상 요청을 보내면 IP가 일정기간 차단된다. 그러나, 일당 10,000건(최소 100분)의 조회는 연간 약 3천건이 공시되는 사업보고서와, 약 3만건이 공시되는 감사보고서를 입수하기에는 충분하다. 친구들에게 부탁하여 api_key를 여러개 확보하여 병렬로 입수한다면 1998년부터 20여년의 공시를 단기간에 모두 입수하는 것도 가능하다.

오픈API의 사용은 <a href="https://github.com/FinanceData/OpenDartReader#opendartreader">OpenDartReader</a>를 사용하는 것이 유용하다.  

DART의 목적이 기업공시이기 때문에, 표준화되지 않는, 아니 표준화 될 수 없는 '외부감사'에 관한 정보와 재무제표 정보를 제한적으로 입수할 수 있다. 이하 설명하는 입수/가공 코드는 이러한 측면에서 OpenAPI를 보완한다.

### From Disclosure to Data
아래의 그림 1에서는 DART 공시내용을 입수, 가공하여 여러가지 목적으로 사용할 수 있도록 변환하는 과정을 보여주고 있다. 

[그림 1] 공시자료에서 가공된 table까지 흐름도

<img src="https://user-images.githubusercontent.com/33425859/123667214-e71a5280-d874-11eb-9abf-4563d0938cd7.png" width="100%"></img>

## 코드 종류
### (A) Disclosure-to-HTML (Python 3)

#### 코드: scraper
DART 공시파일 중, 예를 들면, 사업보고서는 다음과 같은 깊이가 3인 문서 계층 구조를 사용하고 있다.


    - 사업보고서
        - 대표이사의 확인 (*)
        - ... 
    - 감사보고서
        - 독립된 감사인의 감사보고서 (*)
        - (첨부)재무제표 (*)
            - 재무상태표
            - 손익계산서
            - ...
        - ...

입수 코드는 특정일에 공시된 사업보고서 전체를 하나의 HTML로 입수하지 않는다. 모든 계층의 문서가 자신만의 주소를 갖고 있어 서버 요청이 전체 단위에 수행되지 않기 떄문이다. 그렇지만 이 코드가 항상 가장 깊은 단계까지 내려가서 HTML을 긁어오는 것은 아니다. 그렇게 하는 경우 중복 정보를 입수하게 되기도 하지만, 주소를 찾을 때 예외에 취약한 정규표현식을 사용하여야 한다는 점을 고려하였다. 입수와 후처리의 용이성을 고려하여 위 예시의 * 부분을 개별 단위로 입수한다.

한편, HTML로 작성된 다트 공시파일은 CSS로 입혀진 공통 서식과 <img> 태그로 붙혀지는 이미지 파일이 포함되어있다. 입수 코드는 CSS와 이미지는 가져오지 않고, Bare HTML만 입수한다. 본 입수코드와 후속가공의 목적이 공시자료에 포함된 정보의 입수에 있기 때문에 이미지 정보는 불필요하다.

#### 사용방법
Anaconda를 설치하면 따라오는 통합개발환경인 Spyder에 코드를 붙여서 쓴다. Anaconda 설치시 BeautifulSoup, requests 같은 라이브러리가 따라오기 때문에 사용이 간편하다. 이는 이하, Python을 사용한 모든 코드에 동일하다. scraper 코드의 경우 아래 부분을 필요에 맞게 조정하여 입수한다. 필요하다면 코드를 수정하여 코드 실행 후 콘솔에서 필요한 변수를 지정할 수 있다. (설명을 위해 Comment 삭제한다. 이하 python 코드에 대한 설명은 모두 같다.)

    targetYear = "2019"
    startDate = targetYear + "0101"
    endDate = targetYear + "1231"

    reportType = "A001" 

    delay = 1

    path = r"C:\Users\user\Desktop\\" + reportType + "_" + targetYear
    if os.path.exists(path) != True:
        os.makedirs(path)

    i = 1

<표 1> scraper 사용법 설명
변수(예시) | 설명
--- | ---
targetYear = "2019" | 입수하고자 하는 보고서가 등록된 연도
startDate = targetYear + "0101" | 입력된 MMDD 형식의 날짜부터 입수
endDate = targetYear + "1231" | 입력된 MMDD 형식의 날짜까지 입수
reportType = "A001" | 보고서 타입 (A001 사업보고서, A002 반기보고서, A003 분기보고서, F001 감사보고서, F002 연결감사보고서, F004 회계법인사업보고서. 전체 리스트 DART 오픈API 개발가이드, https://github.com/nKiNk/scrapdart 참조)
path = r"C:\Users\user\Desktop\\" + reportType + '\_' + targetYear | 로컬의 다운로드 경로를 지정. 후속 코드에서 해당 경로가 없는 경우 새로 생성
i = 1 | 다트 공시 화면은 조회 대상 리스트를 만들 때 (default로) 15건당 1페이지 생성. 입력값은 페이지 번호이며, 1 page부터 시작. 오류 등 이유로 코드가 중단되는 경우 i 변수에 들어가있는 값을 찾아 넣어서 중단지점의 근처에서 재시작 


#### 입수파일명
파일명은 입수 자료와 (기업개황에서 추출한) 회사의 정보로 구성되어 있다. 아래에 예시 파일과 파일명에 포함된 정보를 설명하는 표를 작성하였다. 

> A001_2019.12.31_대동고려삼_[기재정정]사업보고서_(2019.06)_2019.12.31 [정정] 사업보고서_I.회사의개요_178600_코넥스시장_110111-2481044_기타 식료품 제조업_2002-03-26_06월_.html

<표2: 파일명 설명>
예시 | 설명
--- | ---
A001 | 보고서 타입
2019.12.31 | 공시자료 접수일
대동고려삼 | 회사명
[기재정정]사업보고서 | 공시단위
(2019.06) | 공시자료 회계기간 종료월
2019.12. 31 [정정] 사업보고서 | 공시자료 문서명
I.회사의 개요 | 입수단위
178600 | 종목코드
코넥스시장 | 시장구분
110111-2481044 | 법인등록번호
기타 식료품 제조업 | 업종명
2002-03-26 | 설립일
06월 | 결산월

### (B) AWS-to-Local

#### 코드: -

금융감독원은 DART 서버에 대한 요청을 최대 1분당 100회로 제한하였다. 이는 1회당 0.6회를 초과하는 접근을 허용하지 않는다는 것이다. 제한을 하지 않는 경우, 어떤 경우는 0.6초 미만으로 접근하거나, 아주 긴 입수단위 문서의 경우 (한줄씩 읽어서 쓰기 때문인지) 1초가 넘게 걸리기도 한다. 따라서, (A)의 scraper 코드는 1초에 1회 이상 새로운 문서로 접근하지 않도록 제한을 하였다. 그러나, 기술적으로 잘 알수 없는 사정으로 모든 입수단위를 1초마다 1건씩 빠르게 입수하는 것은 어렵다. 김형준 등(2015)에서 확인한 바와 같이 사업보고서 1건 입수에 적어도 1분 이상의 시간이 소요된다는 점을 고려하면, 1999년부터 20년의 사업보고서, 분기보고서, 반기보고서, 감사보고서, 연결감사보고서 등을 로컬 컴퓨터 1대로 입수하는 것은 시간 소요가 너무 많다. 김형준 등(2015)의 예상 소요 시간인 1,800시간(약 75일)은 이러한 조건에서 측정한 것이다.

이러한 어려움을 해결하기 위해, 실습실 같은 환경에서 컴퓨터를 여러대 활용하여 입수하거나, AWS의 EC2를 여러개 생성하는 방법 등을 활용하여 공시자료를 접수연도별로 동시에(병렬로) 입수하였다. 나는 본 코드를 활용하며 약 3주 정도 기간동안 1998년에서 2020년까지 등록된 감사보고서, 연결감사보고서, 사업보고서, 회계법인사업보고서를 입수하였고, AWS EC2를 최대 12개 활용하여 진행하였다.

AWS에서 입수한 파일은 압축 후 로컬로 옮겨 가공한다. 

### (C) Local에서 Path 생성

#### 코드: -

DART 공시는 (default로) 접수일 단위로 정렬된다. 입수 코드 역시 각각의 보고서를 연단위로 끊어서 입수하고 있다. 이 때, 사업연도 종료일과 보고서 접수일의 차이, 기재정정, 첨부정정 등의 사유로 과거 공시된 보고서를 수정 재접수 등의 사유로, 예를 들면, 2020년 접수된 보고서는 2013년부터 2020년까지 다양한 사업연도 보고서가 포함되어 있다. 

그러나 최종 가공 데이터는 사업연도로 정리할 필요가 있다. 접수일 자체는 보고서의 재무적 특징을 담고 있지 않아 Data 분석의 기준이 되지 못하기 때문이다. 따라서 코드는 보고서, 접수연도 단위로 입수된 보고서 중 필요한 서류(예: 외부감사 실시내용, 감사보고서 본문, 사업보고서 표지 등)를 분리한 경로리스트를 만들고, 이를 연도별로 분할하여 후속 분석에 사용한다. 프로세스의 주 목적에 더하여 입수과정에서 프로세스 중단, 재시작 등의 사유로 중복입수된 경우 파일에 반영된 표식인 'duplicated'가 포함된 경로를 제거한다.

### (D) 사업보고서 표지에서 필요 정보 입수

#### 코드: businessReportCover

사업보고서 표지에는 여러가지 정보가 포함되어 있다. DART의 기업개황 정보는 업데이트된 정보를 보여주고 있기 때문에, 공시 당시의 기업 현황을 정확히 파악하기 위해 사업보고서에서 입수된 정보가 

## 입수 데이터

### (A) Disclosure-to-HTML (Python 3)

2020년 Scraping한 HTML 파일. 등록일 기준으로 요약된 자료이며 후속 가공이 필요하다. 압축파일에 소용량 파일이 다수 포함되어 있다. 반디 소프트(https://www.bandisoft.com/) 의 반디집 사용을 추천한다. 

<표 2> DART에서 입수한 HTML 파일(CSS/Image없음) 입수 경로

[패널 1] 2011년-2020년	
공시기간 | 입수 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서 | F004 회계법인보고서	
:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:	
2020 | - | - | - | - | - | - | -	
2019 | 2020.8.| [1GB](https://bit.ly/31SEzHh) | [591MB](https://bit.ly/31yIQzt) | [903MB](https://bit.ly/3h1qYnb) | [882MB](https://bit.ly/2XTYfJt)  | [100MB](https://bit.ly/2DqYmFA) | [12MB](https://bit.ly/3gCDk55)	
2018 | 2020.8.| [1,005MB](https://bit.ly/2PHSmL1) | [561MB](https://bit.ly/31GpzMj) | [730MB](https://bit.ly/3gQoZSz) | [867MB](https://bit.ly/2PZD5Ft) | [90MB](https://bit.ly/31yHG72) | [8MB](https://bit.ly/2XGIO7z)	
2017 | 2020.8.| [900MB](https://bit.ly/2DNMcqv) | [508MB](https://bit.ly/30LPMKk) | [788MB](https://bit.ly/2PVDVmP) | [785MB](https://bit.ly/2DHpwYV) | [80MB](https://bit.ly/3ihJwjg) | [8MB](https://bit.ly/2XXvnAj)	
2016 | 2020.8.| [840MB](https://bit.ly/33UOazN) | [482MB](https://bit.ly/2DViuiZ) | [750MB](https://bit.ly/3gcU1mG) | [729MB](https://bit.ly/2XW0LyO) | [77MB](https://bit.ly/2PzJgjm) | [9MB](https://bit.ly/3ikLiQP)	
2015 | 2020.8.| [825MB](https://bit.ly/2Y4GSpp) | [458MB](https://bit.ly/3gP8h6b) | [746MB](https://bit.ly/349mC9V) | [694MB](https://bit.ly/346jYBV) | [72MB](https://bit.ly/33HAVT5) | (주1)	
2014 | 2020.8.| [650MB](https://bit.ly/3430KwT) | [376MB](https://bit.ly/2DYkxCX) | [662MB](https://bit.ly/3aBbRyp) | [672MB](https://bit.ly/310sVdZ) | [67MB](https://bit.ly/33JttGV) | (주1)	
2013 | 2020.8.| [601MB](https://bit.ly/343U6Xj) | [374MB](https://bit.ly/3kF1VZs) | [655MB](https://bit.ly/3gf1qBV) | [552MB](https://bit.ly/3iUatdn) | [63MB](https://bit.ly/3a9Dizg) | (주1)	
2012 | 2020.8.| [564MB](https://bit.ly/349exCe) | [327MB](https://bit.ly/2CsB8hO) | [544MB](https://bit.ly/31dZANr) | [522MB](https://bit.ly/3g8NQje) | [61MB](https://bit.ly/3iDuDbk) | (주1)	
2011 | 2020.8.| [455MB](https://bit.ly/2E8neSj) | [336MB](https://bit.ly/2PUzgkW) | [564MB](https://bit.ly/34dYRhb) | [461MB](https://bit.ly/3209Bgs) | [52MB](https://bit.ly/3127QzX) | (주1)	


(주1) 회계법인 사업보고서는 2016년7월 1일부터 공시하였고 따라서 2016년 이전 입수할 수 없음

(주2) A001_2020에 포함되어 있는 "A001_2020.03.30_글로벌텍스프리_사업보고서_(2019.12)_2020.03.30 감사보고서_감사보고서_204620_코스닥시장_110111-5480233_금융 지원 서비스업_2014-07-31_12월_duplicated"가 정상 파일. duplicated가 없는 파일 삭제 후, 정상 파일 duplicated 표시 삭제.

[패널 2] 2001년-2010년	
공시기간 | 입수 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서	
:---:|:---:|:---:|:---:|:---:|:---:|:---:	
2010 | 2020.8. | [446MB](https://bit.ly/3az7R1f) | [256MB](https://bit.ly/3kIOLum) | [423MB](https://bit.ly/3aFVGQk) | [448MB](https://bit.ly/2CLGB3q) | [62MB](https://bit.ly/3h4X7ui) 	
2009 | 2020.8. | [469MB](https://bit.ly/2Q5GDpU) | [252MB](https://bit.ly/3kJtSzn) | [411MB](https://bit.ly/2Qcsase) | [538MB](https://bit.ly/2CFUkbQ) | [74MB](https://bit.ly/3iXQgn1)	
2008 | 2020.8. | [472MB](https://bit.ly/3g8YmqI) | [258MB](https://bit.ly/3gWzjsl) | [431MB](https://bit.ly/3hktG7E) | [528MB](https://bit.ly/34iQ7Gj) | [62MB](https://bit.ly/344xpCs)	
2007 | 2020.8. | [428MB](https://bit.ly/3aEb8fN) | [260MB](https://bit.ly/3iXPdn5) | [453MB](https://bit.ly/2Ec7azw) | [459MB](https://bit.ly/34qN6Uq) | [53MB](https://bit.ly/2E3rcvw)	
2006 | 2020.8. | [440MB](https://bit.ly/2E9QW9P) | [277MB](https://bit.ly/3g5rfnQ) | [421MB](https://bit.ly/2YqWmnU) | [418MB](https://bit.ly/2CPtRc2) | [46MB](https://bit.ly/3asRXpi) 	
2005 | 2020.8. | [420MB](https://bit.ly/2QdOFg8) | [263MB](https://bit.ly/340W6zD) | [399MB](https://bit.ly/32kxdfF) | [373MB](https://bit.ly/2YkZ4Lv) | [40MB](https://bit.ly/3axNEt0)	
2004 | 2020.8. | [563MB](https://bit.ly/2Ek0z63) | [272MB](https://bit.ly/315jdXT) | [550MB](https://bit.ly/3j9C36y) | [342MB](https://bit.ly/3gf4X35) | [36MB](https://bit.ly/2CuVabi)	
2003 | 2020.8. | [374MB](https://bit.ly/32aOAQc) | [240MB](https://bit.ly/2FAOI3X) | [453MB](https://bit.ly/3l6Kkdf) | [291MB](https://bit.ly/3hnQD9W) | [31MB](https://bit.ly/3kWGW4D)	
2002 | 2020.8. | [342MB](https://bit.ly/2YpHuGy) | [210MB](https://bit.ly/3gaVSZ2) | [325MB](https://bit.ly/3lcDumb) | [260MB](https://bit.ly/2FQIqx9) | [27MB](https://bit.ly/3g0LaEC)	
2001 | 2020.8. | [270MB](https://bit.ly/2FIudlN) | [184MB](https://bit.ly/3kYXQiV) | [272MB](https://bit.ly/2EiFskv) | [206MB](https://bit.ly/3j4q0XZ) | [22MB](https://bit.ly/30YkJeo) 	


[패널 3] 1999년-2000년	
공시기간 | 입수 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서	
:---:|:---:|:---:|:---:|:---:|:---:|:---:	
2000 | 2020.8. | [196MB](https://bit.ly/3hcmdr0) | [150MB](https://bit.ly/3iVmP4X) | [272MB](https://bit.ly/3hlwJME) | [131MB](https://bit.ly/3aPWQcn) | [14MB](https://bit.ly/3h3pEA7) 	
1999 | 2020.8. | [179MB](https://bit.ly/3hhccbX) | [70MB](https://bit.ly/3gbYHZU) | (주1) | (주1) | (주1) 	


(주1) 2000년부터 공시됨	


[패널 4] 결합감사보고서	
공시기간 | 입수 | 결합감사보고서 | 설명 	
:---:|:---:|:---:|:---	
전기간 | 2020.8. | [9MB](https://bit.ly/3j8IAOJ) | 2000년부터 2011년까지 공시된 결합감사보고서 	





## 참고 문헌
김형준 박종원 이재원. 2015. 전자공시시스템(DART)을 활용한 국내 텍스트 분석(Textual Analysis) 환경에 관한 연구. 회계저널 24 (4). 199-221
