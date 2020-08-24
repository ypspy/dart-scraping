# DART 공시파일 입수
## 개요
FSS는 오픈API(https://opendart.fss.or.kr/intro/main.do) 에서 Macro Data를 제공하고 있다. 


여기서 제시하는 여러 코드는 FSS 제공 Data의 범위(종류, 기간)를 벗어난 정보가 필요할 때 사용한다.
예를 들면 외부감사실시내역 상 감사시간이나 사업보고서 감사에 관한 사항에 제시되는 감사보수 정보 등의 입수가 필요할 때가 그렇다.

## 코드 종류
### Disclosure-to-HTML (Python 3)

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

코드는 특정일에 공시된 사업보고서 전체를 하나의 HTML로 입수하지 않는다.
가장 큰 이유는 모든 계층의 문서가 자신만의 주소를 갖고 있어 서버 요청이 전체 단위가 아니라는 점에 있다.
그렇지만 이 코드가 가장 깊은 단계까지 내려가서 HTML을 긁어오는 것은 아니다. 
그렇게 하는 경우 중복 정보를 입수하게 되기도 하지만, 주소를 찾을 때 예외에 취약한 정규표현식을 사용하여야 한다는 점을 고려하였다.


결국 입수와 후처리의 용이성을 고려하여 위 예시의 * 부분을 개별 단위로 입수한다.


#### 사용방법
Anaconda를 설치하면 따라오는 통합개발환경인 Spyder에 코드를 붙여서 쓴다. Anaconda 설치시 BeautifulSoup, requests 같은 라이브러리가 따라오기 때문에 사용이 간편하다.
scraper 코드의 아래 부분을 필요에 맞게 조정하여 입수한다. 필요하다면 코드를 수정하여 코드 실행 후 콘솔에서 필요한 변수를 지정할 수 있다. (설명을 위해 Comment 삭제)

    targetYear = "2019"
    startDate = targetYear + "0101"
    endDate = targetYear + "1231"

    reportType = "A001" 

    delay = 1

    path = r"C:\Users\user\Desktop\\" + reportType + "_" + targetYear
    if os.path.exists(path) != True:
        os.makedirs(path)

    i = 1

<표1: 사용법 설명>
변수(예시) | 설명
--- | ---
targetYear = "2019" | 입수하고자 하는 보고서가 등록된 연도
startDate = targetYear + "0101" | 입력된 MMDD 형식의 날짜부터 입수
endDate = targetYear + "1231" | 입력된 MMDD 형식의 날짜까지 입수
reportType = "A001" | 보고서 타입 (A001 사업보고서, A002 반기보고서, A003 분기보고서, F001 감사보고서, F002 연결감사보고서, F004 회계법인사업보고서. 전체 리스트 DART 오픈API 개발가이드, https://github.com/nKiNk/scrapdart 참조)
path = r"C:\Users\user\Desktop\\" + reportType + '\_' + targetYear | 로컬의 다운로드 경로를 지정. 후속 코드에서 해당 경로가 없는 경우 새로 생성
i = 1 | 다트 공시 화면은 조회 대상 리스트를 만들 때 (default로) 15건당 1페이지 생성. 입력값은 페이지 번호이며, 1 page부터 시작. 오류 등 이유로 코드가 중단되는 경우 i 변수에 들어가있는 값을 찾아 넣어서 중단지점의 근처에서 재시작 


#### 입수파일명
파일명은 입수 자료와 회사의 정보로 구성되어 있다. 아래에 예시 파일과 파일명에 포함된 정보를 설명하는 표를 작성하였다.


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


## 입수 데이터
### 설명
아래 표에 위의 코드를 활용하여 입수한 Data를 다운로드 할 수 있는 구글 드라이브 링크가 포함되어 있다.
DART 공시자료의 특성상 정정공시가 될 때 정정전 공시가 포함된다.
이로 인하여 입수기간에 따라 중복정보가 입수될 수 있다.
중복 입수의 경우 위의 파일명에서 입수 단위의 고유키를 조합(예: 법인등록번호+공시일+보고서명)할 수 있으니 중복은 제거 가능하다.
### 입수전략
용량은 크지 않지만, FSS의 접근 허용 수준(Max. 분당 100건)을 준수하며 많으면 10만건이 넘는 아주 작은 .HTML 파일을 입수하는 것은 굉장히 많은 시간이 소요된다.
IP를 달리하는 여러 컴퓨터를 사용해서 병렬로 입수하는 경우 전체 소요시간은 동일하지만 입수기간을 단축할 수 있다. 여기서는 AWS EC2 16대를 사용하였다.

<표3 기간/타입 >

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


# 입수 파일 가공
## 개요
위에서 설명한 절차로 입수된 데이터는 사용 목적에 맞는 전처리를 거쳐야 사용할 수 있다.  
