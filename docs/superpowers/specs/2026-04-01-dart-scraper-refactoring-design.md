# DART Scraper 리팩토링 디자인

**Date:** 2026-04-01
**Status:** Approved

---

## 개요

한국 DART(전자공시시스템) 공시 문서를 수집·파싱하는 Python 파이프라인의 점진적 리팩토링. 기존 동작 방식(각 스크립트 독립 실행)을 유지하면서 구조, 코드 품질, 유지보수성을 개선한다.

---

## 목표

- 하드코딩된 경로를 `config.yaml`로 중앙화
- 중복 유틸리티 함수를 `parsers/common.py`로 통합
- 파일명·디렉토리 구조를 Python 관례에 맞게 재편
- 버그 수정 및 코드 품질 개선
- `requirements.txt` 생성

**범위 외:** js2py 스크래핑 로직 변경, 통합 파이프라인 구축, 대화형 입력 방식 변경

---

## 디렉토리 구조

### 현재
```
dart-scraper/
├── (A) scraper_refactoring.py
├── Dart_Scraper.py
├── app.py
├── (D-1) businessReportCover
├── (D-2-1) auditReportCoverCurrentPeriod
├── (D-2-2) auditReportCoverAuditor
├── (D-3-1) auditReportFirm
├── (D-3-2) auditReportOpinion
├── (D-3-3) auditReportDate
├── (D-3-4) auditReportGAAP
├── (D-4-1) extract_time_information
├── (D-4-2) auditActivity
├── (D-4-3) auditActivity_communication
├── (D-5-1) extract_totalAsset
├── (D-5-2) extract_netIncome
├── (D-5-3) extract_invRec
├── (D-6-1) icReview
├── (D-7-1) extractGovernance
├── (E-1) mergeCSV_period
├── (E-2) mergeCSV_auditor
├── (E-3) mergeCSV_reportdate
├── (E-4) mergeCSV_financials
├── (E-5) auditCommittee
├── (F-5) textClassification.ipynb
├── (G-1) output
└── industry.xlsx
```

### 리팩토링 후
```
dart-scraper/
├── config.yaml                              ← 신규: 경로·파라미터 중앙화
├── requirements.txt                         ← 신규
├── app.py                                   ← 수정: config.yaml 사용
├── scraper/
│   ├── __init__.py
│   └── dart_scraper.py                      ← Dart_Scraper.py 이동 + 수정
├── parsers/
│   ├── __init__.py
│   ├── common.py                            ← 신규: 공통 함수 통합
│   ├── d1_business_report_cover.py
│   ├── d2_1_audit_cover_period.py
│   ├── d2_2_audit_cover_auditor.py
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
│   ├── e3_merge_reportdate.py
│   ├── e4_merge_financials.py
│   └── e5_audit_committee.py
├── notebooks/
│   └── f5_text_classification.ipynb
├── data/
│   └── industry.xlsx
├── output/                                  ← (G-1) output 대체
└── archive/                                 ← 기존 archive + (A) scraper_refactoring.py
```

---

## config.yaml 구조

```yaml
paths:
  working_dir: "E:/workingDirectory"
  output_dir: "C:/Users/ckpys/Desktop/output"
  data_dir: "data"
  report_dirs:
    - "A001_2017"
    - "A001_2018"
    - "A001_2019"
    - "A001_2020"
    - "F001_2017"
    - "F001_2018"
    - "F001_2019"
    - "F001_2020"
    - "F002_2017"
    - "F002_2018"
    - "F002_2019"
    - "F002_2020"

scraper:
  start_date: 20210531
  end_date: 20220531
  report_type: "A001"
  delay_seconds: 1
  max_results_per_page: 15
```

각 스크립트에서 사용:
```python
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
```

---

## parsers/common.py 공통 모듈

D-series 스크립트에서 중복되는 함수들을 통합:

| 함수 | 설명 |
|------|------|
| `col_span_count(soup)` | td/th colspan 반환, 없으면 1 |
| `row_span_count(soup)` | td/th rowspan 반환, 없으면 1 |
| `matrix_generator(table)` | HTML table → 2D list, rowspan/colspan 처리 |
| `load_config(path)` | config.yaml 로드 |
| `build_path_list(dirs, pattern, working_dir)` | glob으로 파일 경로 리스트 생성 |
| `preprocess_df(path_list)` | 파일명 파싱 → DataFrame → 중복 제거 |
| `deduplicate_df(df)` | key 기반 중복 제거 + 정렬 + toDrop 로직 |

각 파서 스크립트는 고유 도메인 로직만 유지:
```python
from parsers.common import load_config, build_path_list, preprocess_df, matrix_generator
```

---

## 버그 수정

| 파일 | 위치 | 문제 | 수정 |
|------|------|------|------|
| `Dart_Scraper.py` | line 178 | `time.delay(3)` — 존재하지 않는 메서드 | `time.sleep(3)` |
| `(D-1) businessReportCover` | line 76 | `container(...)` — 리스트를 함수처럼 호출 | `container.append(...)` |

---

## 코드 품질 개선

| 항목 | 현재 | 변경 |
|------|------|------|
| 함수명 | `PascalCase` (`Document_Address_Parser`) | `snake_case` (`document_address_parser`) |
| while 루프 | 수동 인덱스 증가 (`loop += 6`) | `for` 루프로 교체 가능한 경우 변경 |
| magic string | `href[28:36]` 등 | 상수명 또는 인라인 주석으로 의도 명시 |
| 재귀 호출 | `app.py` 에러 후 재귀 호출 | `while` 루프로 교체 (스택 오버플로 방지) |

---

## requirements.txt

```
requests
beautifulsoup4
js2py
tqdm
pandas
numpy
pyyaml
lxml
openpyxl
```

---

## 변경하지 않는 것

- js2py 기반 스크래핑 로직
- 각 파서의 DART 도메인 파싱 로직
- app.py의 대화형 입력 방식 (chdir, input())
- 각 스크립트의 독립 실행 가능성
