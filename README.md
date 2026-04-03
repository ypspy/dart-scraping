# DART 공시파일 입수 및 가공

## 개요

금융감독원 전자공시시스템(DART)에서 사업보고서 및 감사보고서 HTML을 수집하고, 감사 관련 정보(감사인, 감사의견, 지배구조 등)를 추출하여 분석용 데이터셋으로 가공하는 파이프라인입니다.

DART 오픈API는 일 10,000건 한도가 있습니다. 본 스크레이퍼는 API를 사용하지 않고 DART 공시 웹페이지에서 HTML을 직접 수집합니다.

## 디렉토리 구조

```
dart-scraper/
├── app.py                  # 스크레이퍼 실행 진입점
├── config.yaml             # 경로 및 스크레이퍼 설정
├── requirements.txt        # 의존 패키지 목록
├── scraper/
│   ├── __init__.py
│   └── dart_scraper.py     # DART 페이지 순회 및 HTML 저장
├── parsers/
│   ├── __init__.py
│   ├── common.py           # 공통 유틸리티 함수
│   ├── d1_business_report_cover.py
│   ├── d2_1_audit_report_cover_period.py
│   ├── d2_2_audit_report_cover_auditor.py
│   ├── d3_1_audit_firm.py
│   ├── d3_2_audit_opinion.py
│   ├── d3_3_audit_date.py
│   ├── d3_4_audit_gaap.py
│   ├── d4_1_time_information.py
│   ├── d4_2_audit_activity.py
│   ├── d4_3_audit_activity_communication.py
│   ├── d5_1_total_asset.py
│   ├── d5_2_net_income.py
│   ├── d5_3_inv_rec.py
│   ├── d6_1_ic_review.py
│   └── d7_1_governance.py
├── merge/
│   ├── __init__.py
│   ├── e1_merge_period.py
│   ├── e2_merge_auditor.py
│   ├── e3_merge_report_date.py
│   ├── e4_merge_financials.py
│   └── e5_audit_committee.py
├── tests/
│   └── test_common.py      # parsers/common.py 단위 테스트 (17개)
├── data/                   # 보조 데이터 (감사인 목록 등)
├── output/                 # 가공 결과 CSV 저장 위치
└── archive/                # 리팩토링 이전 레거시 코드
```

## 설치

```bash
pip install -r requirements.txt
```

Tesseract OCR이 필요합니다 (d7_1_governance.py 실행 시).
- Windows: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 에서 설치 후 환경변수에 `C:\Program Files\Tesseract-OCR` 추가

## 설정 (config.yaml)

```yaml
paths:
  working_dir: "E:/workingDirectory"   # 수집된 HTML 파일이 있는 루트 경로
  output_dir: "C:/Users/.../output"    # 파싱 결과 CSV 저장 경로
  data_dir: "data"                     # 보조 데이터 경로 (감사인 목록 등)
  governance_dir: "C:/data"            # 정관 HTML 경로 (d4_2, d7_1 전용)
  report_dirs:                         # working_dir 하위의 보고서 폴더 목록
    - "A001_2017"
    - "F001_2019"
    # ...

scraper:
  delay_seconds: 300    # 연결 오류 발생 시 재시도 대기 시간(초)
```

`working_dir` 하위에 `A001_2017/`, `F001_2019/` 등 연도별 폴더를 생성하고 HTML 파일을 위치시킵니다.

## 사용법

### 1단계: HTML 수집 (Scraping)

```bash
python app.py
```

실행 시 다음을 입력합니다:
- 저장 경로 (예: `E:/A001_2019`)
- 보고서 타입 (예: `A001`)
- 수집 시작일 (예: `20190101`)
- 수집 종료일 (예: `20191231`)
- 시작 페이지 번호 (보통 `1`, 중단 후 재개 시 마지막 페이지 번호)

### 2단계: 파싱 (Parsing)

`config.yaml`에서 경로를 설정한 후 각 파서를 실행합니다:

```bash
python parsers/d1_business_report_cover.py
python parsers/d3_1_audit_firm.py
# ...
```

각 파서는 `output_dir`에 CSV 파일을 생성합니다.

### 3단계: 병합 (Merging)

```bash
python merge/e1_merge_period.py
python merge/e2_merge_auditor.py
# ...
```

## 파이프라인 구성

| 단계 | 스크립트 | 입력 | 출력 |
|------|---------|------|------|
| A | `app.py` + `scraper/dart_scraper.py` | DART 웹 | HTML 파일 |
| D-1 | `d1_business_report_cover.py` | A001 HTML | wp01.data01.output.csv |
| D-2-1 | `d2_1_audit_report_cover_period.py` | F001 HTML | wp01.data02.output.csv |
| D-2-2 | `d2_2_audit_report_cover_auditor.py` | F001 HTML | wp01.data03.output.csv |
| D-3-1 | `d3_1_audit_firm.py` | F001 HTML | wp01.data05.output.csv |
| D-3-2 | `d3_2_audit_opinion.py` | F001 HTML | wp01.data06.output.csv |
| D-3-3 | `d3_3_audit_date.py` | F001 HTML | wp01.data07.output.csv |
| D-3-4 | `d3_4_audit_gaap.py` | F001 HTML | wp01.data08.output.csv |
| D-4-1 | `d4_1_time_information.py` | A001 HTML | wp01.data09.output.csv |
| D-4-2 | `d4_2_audit_activity.py` | A001 HTML | wp01.data10.output.csv |
| D-4-3 | `d4_3_audit_activity_communication.py` | A001 HTML | wp01.data11.output.csv |
| D-5-1 | `d5_1_total_asset.py` | F001 HTML | wp01.data12.output.csv |
| D-5-2 | `d5_2_net_income.py` | F001 HTML | wp01.data13.output.csv |
| D-5-3 | `d5_3_inv_rec.py` | F001 HTML | wp01.data14.output.csv |
| D-6-1 | `d6_1_ic_review.py` | A001 HTML | wp01.data15.output.csv |
| D-7-1 | `d7_1_governance.py` | 정관 HTML | wp01.data20.output.csv |
| E-1 | `e1_merge_period.py` | D-1, D-4-1 | 결합 데이터셋 |
| E-2 | `e2_merge_auditor.py` | D-2-2, D-3-1 | 결합 데이터셋 |
| E-3 | `e3_merge_report_date.py` | D-3-3 등 | 결합 데이터셋 |
| E-4 | `e4_merge_financials.py` | D-5-1~3 | 결합 데이터셋 |
| E-5 | `e5_audit_committee.py` | D-4-2, D-7-1 | 결합 데이터셋 |

## 입수 파일명 형식

수집된 HTML 파일명은 다음 정보를 포함합니다:

```
A001_2019.12.31_회사명_[기재정정]사업보고서_(2019.06)_문서명_섹션명_종목코드_시장구분_법인등록번호_업종명_설립일_결산월_.html
```

| 항목 | 예시 |
|------|------|
| 보고서 타입 | `A001` |
| 접수일 | `2019.12.31` |
| 회사명 | `대동고려삼` |
| 공시단위 | `[기재정정]사업보고서` |
| 회계기간 | `(2019.06)` |
| 문서명 | `2019.12.31 사업보고서` |
| 입수단위(섹션) | `I.회사의개요` |
| 종목코드 | `178600` |
| 시장구분 | `코넥스시장` |
| 법인등록번호 | `110111-2481044` |
| 업종명 | `기타 식료품 제조업` |
| 설립일 | `2002-03-26` |
| 결산월 | `06월` |

## 보고서 타입 코드

| 코드 | 설명 |
|------|------|
| A001 | 사업보고서 |
| A002 | 반기보고서 |
| A003 | 분기보고서 |
| F001 | 감사보고서 |
| F002 | 연결감사보고서 |
| F004 | 회계법인사업보고서 |

## 수집 데이터 다운로드

2020년 수집한 HTML 파일(CSS/Image 없음)입니다.

**[패널 1] 2011년–2020년**

| 공시기간 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서 | F004 회계법인보고서 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 2019 | [1GB](https://bit.ly/31SEzHh) | [591MB](https://bit.ly/31yIQzt) | [903MB](https://bit.ly/3h1qYnb) | [882MB](https://bit.ly/2XTYfJt) | [100MB](https://bit.ly/2DqYmFA) | [12MB](https://bit.ly/3gCDk55) |
| 2018 | [1,005MB](https://bit.ly/2PHSmL1) | [561MB](https://bit.ly/31GpzMj) | [730MB](https://bit.ly/3gQoZSz) | [867MB](https://bit.ly/2PZD5Ft) | [90MB](https://bit.ly/31yHG72) | [8MB](https://bit.ly/2XGIO7z) |
| 2017 | [900MB](https://bit.ly/2DNMcqv) | [508MB](https://bit.ly/30LPMKk) | [788MB](https://bit.ly/2PVDVmP) | [785MB](https://bit.ly/2DHpwYV) | [80MB](https://bit.ly/3ihJwjg) | [8MB](https://bit.ly/2XXvnAj) |
| 2016 | [840MB](https://bit.ly/33UOazN) | [482MB](https://bit.ly/2DViuiZ) | [750MB](https://bit.ly/3gcU1mG) | [729MB](https://bit.ly/2XW0LyO) | [77MB](https://bit.ly/2PzJgjm) | [9MB](https://bit.ly/3ikLiQP) |
| 2015 | [825MB](https://bit.ly/2Y4GSpp) | [458MB](https://bit.ly/3gP8h6b) | [746MB](https://bit.ly/349mC9V) | [694MB](https://bit.ly/346jYBV) | [72MB](https://bit.ly/33HAVT5) | (주1) |
| 2014 | [650MB](https://bit.ly/3430KwT) | [376MB](https://bit.ly/2DYkxCX) | [662MB](https://bit.ly/3aBbRyp) | [672MB](https://bit.ly/310sVdZ) | [67MB](https://bit.ly/33JttGV) | (주1) |
| 2013 | [601MB](https://bit.ly/343U6Xj) | [374MB](https://bit.ly/3kF1VZs) | [655MB](https://bit.ly/3gf1qBV) | [552MB](https://bit.ly/3iUatdn) | [63MB](https://bit.ly/3a9Dizg) | (주1) |
| 2012 | [564MB](https://bit.ly/349exCe) | [327MB](https://bit.ly/2CsB8hO) | [544MB](https://bit.ly/31dZANr) | [522MB](https://bit.ly/3g8NQje) | [61MB](https://bit.ly/3iDuDbk) | (주1) |
| 2011 | [455MB](https://bit.ly/2E8neSj) | [336MB](https://bit.ly/2PUzgkW) | [564MB](https://bit.ly/34dYRhb) | [461MB](https://bit.ly/3209Bgs) | [52MB](https://bit.ly/3127QzX) | (주1) |

(주1) F004 회계법인사업보고서는 2016년 7월 1일부터 공시

**[패널 2] 2001년–2010년**

| 공시기간 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 2010 | [446MB](https://bit.ly/3az7R1f) | [256MB](https://bit.ly/3kIOLum) | [423MB](https://bit.ly/3aFVGQk) | [448MB](https://bit.ly/2CLGB3q) | [62MB](https://bit.ly/3h4X7ui) |
| 2009 | [469MB](https://bit.ly/2Q5GDpU) | [252MB](https://bit.ly/3kJtSzn) | [411MB](https://bit.ly/2Qcsase) | [538MB](https://bit.ly/2CFUkbQ) | [74MB](https://bit.ly/3iXQgn1) |
| 2008 | [472MB](https://bit.ly/3g8YmqI) | [258MB](https://bit.ly/3gWzjsl) | [431MB](https://bit.ly/3hktG7E) | [528MB](https://bit.ly/34iQ7Gj) | [62MB](https://bit.ly/344xpCs) |
| 2007 | [428MB](https://bit.ly/3aEb8fN) | [260MB](https://bit.ly/3iXPdn5) | [453MB](https://bit.ly/2Ec7azw) | [459MB](https://bit.ly/34qN6Uq) | [53MB](https://bit.ly/2E3rcvw) |
| 2006 | [440MB](https://bit.ly/2E9QW9P) | [277MB](https://bit.ly/3g5rfnQ) | [421MB](https://bit.ly/2YqWmnU) | [418MB](https://bit.ly/2CPtRc2) | [46MB](https://bit.ly/3asRXpi) |
| 2005 | [420MB](https://bit.ly/2QdOFg8) | [263MB](https://bit.ly/340W6zD) | [399MB](https://bit.ly/32kxdfF) | [373MB](https://bit.ly/2YkZ4Lv) | [40MB](https://bit.ly/3axNEt0) |
| 2004 | [563MB](https://bit.ly/2Ek0z63) | [272MB](https://bit.ly/315jdXT) | [550MB](https://bit.ly/3j9C36y) | [342MB](https://bit.ly/3gf4X35) | [36MB](https://bit.ly/2CuVabi) |
| 2003 | [374MB](https://bit.ly/32aOAQc) | [240MB](https://bit.ly/2FAOI3X) | [453MB](https://bit.ly/3l6Kkdf) | [291MB](https://bit.ly/3hnQD9W) | [31MB](https://bit.ly/3kWGW4D) |
| 2002 | [342MB](https://bit.ly/2YpHuGy) | [210MB](https://bit.ly/3gaVSZ2) | [325MB](https://bit.ly/3lcDumb) | [260MB](https://bit.ly/2FQIqx9) | [27MB](https://bit.ly/3g0LaEC) |
| 2001 | [270MB](https://bit.ly/2FIudlN) | [184MB](https://bit.ly/3kYXQiV) | [272MB](https://bit.ly/2EiFskv) | [206MB](https://bit.ly/3j4q0XZ) | [22MB](https://bit.ly/30YkJeo) |

**[패널 3] 1999년–2000년**

| 공시기간 | A001 사업보고서 | A002 반기보고서 | A003 분기보고서 | F001 감사보고서 | F002 연결보고서 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 2000 | [196MB](https://bit.ly/3hcmdr0) | [150MB](https://bit.ly/3iVmP4X) | [272MB](https://bit.ly/3hlwJME) | [131MB](https://bit.ly/3aPWQcn) | [14MB](https://bit.ly/3h3pEA7) |
| 1999 | [179MB](https://bit.ly/3hhccbX) | [70MB](https://bit.ly/3gbYHZU) | (주2) | (주2) | (주2) |

(주2) A003, F001, F002는 2000년부터 공시

**[패널 4] 결합감사보고서**

| 공시기간 | 파일 | 설명 |
|:---:|:---:|:---|
| 전기간 | [9MB](https://bit.ly/3j8IAOJ) | 2000년–2011년 결합감사보고서 |

## 참고 문헌

김형준 박종원 이재원. 2015. 전자공시시스템(DART)을 활용한 국내 텍스트 분석(Textual Analysis) 환경에 관한 연구. 회계저널 24 (4). 199-221
