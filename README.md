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

## 참고 문헌

김형준 박종원 이재원. 2015. 전자공시시스템(DART)을 활용한 국내 텍스트 분석(Textual Analysis) 환경에 관한 연구. 회계저널 24 (4). 199-221
