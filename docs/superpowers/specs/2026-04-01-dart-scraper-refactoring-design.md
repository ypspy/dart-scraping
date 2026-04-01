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
├── app.py                                   ← 수정: config.yaml 사용, 재귀→while
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
└── archive/                                 ← 기존 archive + (A) scraper_refactoring.py 이동
```

**참고:** `(A) scraper_refactoring.py`는 `Dart_Scraper.py`의 초기 프로토타입으로 `archive/`로 이동한다. 이 파일 이동은 구현 작업의 일부로 포함된다 (사전 수동 작업이 아님).

---

## config.yaml 구조

```yaml
paths:
  working_dir: "E:/workingDirectory"        # 파서 스크립트의 HTML 파일 루트 경로
  output_dir: "C:/Users/ckpys/Desktop/output"  # CSV 출력 경로 (기존 yoont → ckpys로 변경)
  data_dir: "data"
  governance_dir: "C:/data"                 # d7_1_governance 전용 (별도 경로 사용)
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
from pathlib import Path

CONFIG_PATH = Path(__file__).parents[1] / "config.yaml"  # 프로젝트 루트 기준
with open(CONFIG_PATH) as f:
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
| `find_target_table(soup)` | 대상 table 1개 반환 (td > 20 조건) |
| `find_all_tables(soup)` | 모든 table 리스트 반환 |
| `load_config(path)` | config.yaml 로드 |
| `build_path_list(working_dir, report_dirs, pattern)` | glob으로 파일 경로 리스트 생성 |
| `preprocess_df(path_list)` | 파일명 파싱 → DataFrame → key 컬럼 추가 |
| `deduplicate_df(df)` | key 기반 중복 제거 + 정렬 + toDrop 로직 |

**`find_target_table` vs `find_all_tables` 사용 구분:**

- `find_target_table(soup)` (단일 table, td > 20): `d4_1`, `d5_1`, `d5_2`, `d5_3`, `d6_1`
- `find_all_tables(soup)` (전체 table 리스트): `d1`, `d3_1`, `d7_1`

각 파서 스크립트는 고유 도메인 로직만 유지:
```python
from parsers.common import load_config, build_path_list, preprocess_df, matrix_generator
```

### 독립 실행 시 sys.path 처리

파서(`parsers/`) 및 병합(`merge/`) 스크립트 모두 상단에 아래를 추가:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))  # 프로젝트 루트를 sys.path에 추가
```

이렇게 하면 `python parsers/d1_business_report_cover.py` 또는 `python merge/e1_merge_period.py` 등 어느 위치에서 실행해도 `from parsers.common import ...`가 동작한다.

### 신규 함수 인터페이스

`load_config`, `build_path_list`, `preprocess_df`, `deduplicate_df`는 기존 인라인 코드를 추출·일반화한 신규 함수다.

```python
def load_config(path: Path = None) -> dict:
    """
    config.yaml 로드.
    path가 None이면 Path(__file__).parents[1] / "config.yaml" 사용 (프로젝트 루트 기준).
    """

def build_path_list(working_dir: str, report_dirs: list[str], pattern: str) -> list[str]:
    """
    각 report_dir에서 glob 패턴으로 파일 경로 수집.
    "duplicated" 포함 파일 제거.
    연도 필터링(예: "(2017." 포함 여부)은 각 파서 스크립트에서 호출 후 처리한다.
    이유: 연도 범위가 파서마다 다르기 때문 (D-1은 2017~2019, D-4-2는 2014~2019 등).
    """

def preprocess_df(path_list: list[str]) -> pd.DataFrame:
    """
    파일명을 '_' 기준으로 분리해 DataFrame 생성.
    con(연결/별도), amend(정정/원본), key 컬럼 추가.
    key = df[2] + df[6].str.slice(stop=10) + con + amend + df[5] + df[8] + df[10]
    (접수일 + 제출일 + 연결여부 + 정정여부 + 보고기간종료월 + 종목코드 + 법인등록번호)
    중복 제거(drop_duplicates)는 포함. path 컬럼은 "path"로 명시적 추가.
    반환 DataFrame에는 중복 제거 전 isTrue(중복 항목) 보존하지 않음.
    """

def deduplicate_df(df: pd.DataFrame, sort_cols: list, key_cols: list[str]) -> pd.DataFrame:
    """
    key 기반 중복 제거 후 정렬 및 toDrop 로직.
    - sort_cols: 정렬 기준 컬럼명 리스트 (호출자가 지정).
    - key_cols: toDrop 비교에 사용할 컬럼명 2개 (호출자가 지정).
      대부분 스크립트에서 [df[3]에 해당하는 컬럼, df[8]에 해당하는 컬럼]이나,
      drop() 순서에 따라 실제 컬럼명이 달라지므로 호출자가 명시적으로 전달.
    - toDrop 로직: key_cols[0]과 key_cols[1]이 이전 행과 동일하면 toDrop 누적,
      아니면 1로 초기화. 최종적으로 toDrop == 1인 행만 유지.
    - df.iloc 위치 기반 접근 금지. df.loc[idx, col] 레이블 기반으로만 접근.
    이유: 스크립트마다 drop() 순서와 컬럼 수가 달라 위치 인덱스가 일치하지 않음.
    """
```

---

## 버그 수정

| 파일 | 위치 | 문제 | 수정 |
|------|------|------|------|
| `Dart_Scraper.py` | line 178 | `time.delay(3)` — 존재하지 않는 메서드 | `time.sleep(3)` |
| `(D-1)`, `(D-2-1)`, `(D-2-2)`, `(D-3-1)`, `(D-3-2)`, `(D-3-3)`, `(D-3-4)`, `(D-5-1)`, `(D-6-1)` | `ParsingTime()` else 분기 (각 line 76~77) | `container(...)` — 리스트를 함수처럼 호출 | `container.append(...)`. `parsers/common.py`로 통합 시 일괄 수정됨 |
| `app.py` | line 40 | `app(i, query)` 재귀 호출 — 지속적 네트워크 오류 시 스택 오버플로 발생. 현재 페이지 번호 `i`를 보존하며 재시도하는 구조를 `while True` 루프로 교체해야 함 | `while True` 루프로 교체. 에러 발생 시 현재 `i` 유지하고 sleep 후 계속 |

---

## 코드 품질 개선

| 항목 | 현재 | 변경 |
|------|------|------|
| 함수명 (`scraper/`) | `PascalCase` (`Document_Address_Parser`) | `snake_case` (`document_address_parser`) |
| 함수명 (`parsers/common.py`) | `PascalCase` (`MatrixGenerator`, `FindTargetTable`) | `snake_case` (`matrix_generator`, `find_target_table`) |
| 함수명 (각 파서 스크립트 내 고유 함수: `ParsingTime`, `Indexing` 등) | `PascalCase` | `snake_case`. 각 파서 내 모든 호출 지점도 함께 변경 |
| while 루프 | 수동 인덱스 증가 (`loop += 6`) | `for` 루프로 교체 가능한 경우 변경 |
| magic string | `href[28:36]` 등 | 상수명 또는 인라인 주석으로 의도 명시 |

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
jupyter
pytesseract
scikit-image
opencv-python
```

`pytesseract`, `scikit-image`, `opencv-python`은 `d7_1_governance.py`(OCR 기반 거버넌스 파서)에서 사용.

---

## 변경하지 않는 것

- js2py 기반 스크래핑 로직
- 각 파서의 DART 도메인 파싱 로직
- `app.py`의 대화형 입력 방식 (`chdir`, `input()`)
- 각 스크립트의 독립 실행 가능성
