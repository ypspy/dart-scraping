# DART Scraper 리팩토링 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 파일 구조를 Python 패키지로 재편하고, 공통 유틸리티를 통합하며, 하드코딩된 경로를 config.yaml로 중앙화하고, 버그를 수정한다.

**Architecture:** 독립 실행 가능한 스크립트 구조를 유지하면서 `parsers/common.py`에 공통 함수를 통합하고, 각 스크립트 상단에 `sys.path` 처리를 추가해 패키지 import를 가능하게 한다. 모든 경로·파라미터는 프로젝트 루트의 `config.yaml`에서 읽는다.

**Tech Stack:** Python 3, pytest, pyyaml, beautifulsoup4, pandas, requests, js2py, tqdm, pytesseract, scikit-image, opencv-python

**Spec:** `docs/superpowers/specs/2026-04-01-dart-scraper-refactoring-design.md`

---

## File Map

| 파일 | 작업 |
|------|------|
| `config.yaml` | 신규 생성 |
| `requirements.txt` | 신규 생성 |
| `app.py` | 수정 (재귀→while, config 사용) |
| `scraper/__init__.py` | 신규 생성 (빈 파일) |
| `scraper/dart_scraper.py` | `Dart_Scraper.py` 이동 + snake_case + 버그 수정 |
| `parsers/__init__.py` | 신규 생성 (빈 파일) |
| `parsers/common.py` | 신규 생성 (공통 함수 통합) |
| `parsers/d1_business_report_cover.py` | `(D-1)` 이동 + 수정 |
| `parsers/d2_1_audit_cover_period.py` | `(D-2-1)` 이동 + 수정 |
| `parsers/d2_2_audit_cover_auditor.py` | `(D-2-2)` 이동 + 수정 |
| `parsers/d3_1_audit_firm.py` | `(D-3-1)` 이동 + 수정 |
| `parsers/d3_2_audit_opinion.py` | `(D-3-2)` 이동 + 수정 |
| `parsers/d3_3_audit_date.py` | `(D-3-3)` 이동 + 수정 |
| `parsers/d3_4_audit_gaap.py` | `(D-3-4)` 이동 + 수정 |
| `parsers/d4_1_time_information.py` | `(D-4-1)` 이동 + 수정 |
| `parsers/d4_2_audit_activity.py` | `(D-4-2)` 이동 + 수정 |
| `parsers/d4_3_audit_activity_communication.py` | `(D-4-3)` 이동 + 수정 |
| `parsers/d5_1_total_asset.py` | `(D-5-1)` 이동 + 수정 |
| `parsers/d5_2_net_income.py` | `(D-5-2)` 이동 + 수정 |
| `parsers/d5_3_inv_rec.py` | `(D-5-3)` 이동 + 수정 |
| `parsers/d6_1_ic_review.py` | `(D-6-1)` 이동 + 수정 |
| `parsers/d7_1_governance.py` | `(D-7-1)` 이동 + 수정 |
| `merge/__init__.py` | 신규 생성 (빈 파일) |
| `merge/e1_merge_period.py` | `(E-1)` 이동 + 수정 |
| `merge/e2_merge_auditor.py` | `(E-2)` 이동 + 수정 |
| `merge/e3_merge_reportdate.py` | `(E-3)` 이동 + 수정 |
| `merge/e4_merge_financials.py` | `(E-4)` 이동 + 수정 |
| `merge/e5_audit_committee.py` | `(E-5)` 이동 + 수정 |
| `notebooks/f5_text_classification.ipynb` | `(F-5)` 이동 |
| `data/industry.xlsx` | `industry.xlsx` 이동 |
| `output/` | `(G-1) output` 대체 폴더 |
| `archive/(A) scraper_refactoring.py` | 프로토타입 이동 |
| `tests/test_common.py` | 신규 생성 (공통 함수 단위 테스트) |

---

## Task 1: 디렉토리 스캐폴딩 + requirements.txt + config.yaml

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml`
- Create: `scraper/__init__.py`
- Create: `parsers/__init__.py`
- Create: `merge/__init__.py`
- Create: `notebooks/` (폴더)
- Create: `data/` (폴더)
- Create: `output/` (폴더)
- Create: `tests/` (폴더)
- Move: `(A) scraper_refactoring.py` → `archive/(A) scraper_refactoring.py`
- Move: `(G-1) output` → `output/` (내용이 있다면)
- Move: `(F-5) textClassification.ipynb` → `notebooks/f5_text_classification.ipynb`
- Move: `industry.xlsx` → `data/industry.xlsx`

- [ ] **Step 1: 폴더 및 `__init__.py` 생성**

```bash
mkdir -p scraper parsers merge notebooks data output tests
touch scraper/__init__.py parsers/__init__.py merge/__init__.py
```

- [ ] **Step 2: `pytest.ini` 생성 (archive/ 제외)**

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 3: `requirements.txt` 생성**

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
pytest
```

- [ ] **Step 4: `config.yaml` 생성**

```yaml
paths:
  working_dir: "E:/workingDirectory"
  output_dir: "C:/Users/ckpys/Desktop/output"
  data_dir: "data"
  governance_dir: "C:/data"  # d4_2_audit_activity + d7_1_governance 공용 (두 파서 모두 C:/data 사용)
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

- [ ] **Step 5: 파일 이동**

```bash
# 프로토타입 → archive
mv "(A) scraper_refactoring.py" archive/

# 노트북, 데이터, 출력 이동
mv "(F-5) textClassification.ipynb" notebooks/f5_text_classification.ipynb
mv industry.xlsx data/industry.xlsx
# (G-1) output 내용 있으면: mv "(G-1) output" output/ (없으면 output/ 폴더만 존재)
```

- [ ] **Step 6: 커밋**

```bash
git add .
git commit -m "chore: scaffold directory structure and add config/requirements"
```

---

## Task 2: `parsers/common.py` — TDD로 공통 모듈 구현

**Files:**
- Create: `tests/test_common.py`
- Create: `parsers/common.py`

이 task는 TDD로 진행: 각 함수마다 테스트 먼저 작성 → 실패 확인 → 구현 → 통과 확인.

### 2a. col_span_count / row_span_count

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_common.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from bs4 import BeautifulSoup
from parsers.common import col_span_count, row_span_count

def make_tag(html):
    return BeautifulSoup(html, "html.parser").find("td")

def test_col_span_count_default():
    tag = make_tag("<td>x</td>")
    assert col_span_count(tag) == 1

def test_col_span_count_explicit():
    tag = make_tag('<td colspan="3">x</td>')
    assert col_span_count(tag) == 3

def test_row_span_count_default():
    tag = make_tag("<td>x</td>")
    assert row_span_count(tag) == 1

def test_row_span_count_explicit():
    tag = make_tag('<td rowspan="2">x</td>')
    assert row_span_count(tag) == 2
```

- [ ] **Step 2: 실패 확인**

```bash
pytest tests/test_common.py -v
```
Expected: `ImportError` 또는 `ModuleNotFoundError`

- [ ] **Step 3: `parsers/common.py` 생성 — col/row span 구현**

```python
# parsers/common.py
from __future__ import annotations
import glob
import os
from pathlib import Path
import pandas as pd
import yaml
from bs4 import BeautifulSoup, Tag


def col_span_count(soup: Tag) -> int:
    """td/th의 colspan 값 반환. 없으면 1."""
    try:
        return int(soup["colspan"])
    except KeyError:
        return 1


def row_span_count(soup: Tag) -> int:
    """td/th의 rowspan 값 반환. 없으면 1."""
    try:
        return int(soup["rowspan"])
    except KeyError:
        return 1
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_common.py::test_col_span_count_default tests/test_common.py::test_col_span_count_explicit tests/test_common.py::test_row_span_count_default tests/test_common.py::test_row_span_count_explicit -v
```
Expected: 4 passed

### 2b. matrix_generator

- [ ] **Step 5: 테스트 추가**

```python
def test_matrix_generator_simple():
    html = """
    <table>
      <tr><td>A</td><td>B</td></tr>
      <tr><td>C</td><td>D</td></tr>
    </table>"""
    table = BeautifulSoup(html, "html.parser").find("table")
    from parsers.common import matrix_generator
    result = matrix_generator(table)
    assert result == [["A", "B"], ["C", "D"]]

def test_matrix_generator_colspan():
    html = """
    <table>
      <tr><td colspan="2">AB</td></tr>
      <tr><td>C</td><td>D</td></tr>
    </table>"""
    table = BeautifulSoup(html, "html.parser").find("table")
    from parsers.common import matrix_generator
    result = matrix_generator(table)
    assert result[0] == ["AB", "AB"]
    assert result[1] == ["C", "D"]

def test_matrix_generator_rowspan():
    html = """
    <table>
      <tr><td rowspan="2">A</td><td>B</td></tr>
      <tr><td>C</td></tr>
    </table>"""
    table = BeautifulSoup(html, "html.parser").find("table")
    from parsers.common import matrix_generator
    result = matrix_generator(table)
    assert result[0][0] == "A"
    assert result[1][0] == "A"  # rowspan으로 복사됨
    assert result[1][1] == "C"

def test_matrix_generator_rowspan_and_colspan():
    # 3컬럼 테이블: 1행=[rowspan2+colspan2 셀 "X", 일반 "Y"], 2행=[일반 "Z"]
    html = """
    <table>
      <tr><td rowspan="2" colspan="2">X</td><td>Y</td></tr>
      <tr><td>Z</td></tr>
    </table>"""
    table = BeautifulSoup(html, "html.parser").find("table")
    from parsers.common import matrix_generator
    result = matrix_generator(table)
    # 1행: [X, X, Y]
    assert result[0] == ["X", "X", "Y"]
    # 2행: [X, X, Z] — rowspan으로 첫 두 컬럼은 X 복사
    assert result[1][0] == "X"
    assert result[1][1] == "X"
    assert result[1][2] == "Z"
```

- [ ] **Step 6: 실패 확인**

```bash
pytest tests/test_common.py -v -k "matrix"
```
Expected: `ImportError` (matrix_generator 미구현)

- [ ] **Step 7: matrix_generator 구현 추가**

```python
def matrix_generator(table: Tag) -> list[list[str]]:
    """HTML table → 2D list. rowspan/colspan 처리."""
    table_rows = table.find_all("tr")
    column_count = 0
    for row in table_rows:
        col_num = 0
        for cell in row.find_all(["th", "td"]):
            try:
                col_num += int(cell["colspan"])
            except KeyError:
                col_num += 1
            if col_num > column_count:
                column_count = col_num
    row_count = len(table_rows)
    matrix = [["#"] * column_count for _ in range(row_count)]

    for i, row in enumerate(table_rows):
        locator = [j for j, x in enumerate(matrix[i]) if x == "#"]
        col_span_offset = 0
        for cell in row.find_all(["th", "td"]):
            rs = row_span_count(cell)
            cs = col_span_count(cell)
            for k in range(rs):
                for l in range(cs):
                    matrix[i + k][locator[l + col_span_offset]] = cell.text.strip()
            col_span_offset += cs
    return matrix
```

- [ ] **Step 8: 테스트 통과**

```bash
pytest tests/test_common.py -v -k "matrix"
```
Expected: 3 passed

### 2c. find_target_table / find_all_tables

- [ ] **Step 9: 테스트 추가**

```python
def test_find_target_table_returns_first_large():
    html = """
    <body>
      <table><tr><td>small</td></tr></table>
      <table>""" + "<tr><td>x</td></tr>" * 25 + """</table>
    </body>"""
    soup = BeautifulSoup(html, "html.parser")
    from parsers.common import find_target_table
    result = find_target_table(soup)
    assert len(result.find_all("td")) > 20

def test_find_all_tables_returns_list():
    html = "<body><table><tr><td>a</td></tr></table><table><tr><td>b</td></tr></table></body>"
    soup = BeautifulSoup(html, "html.parser")
    from parsers.common import find_all_tables
    result = find_all_tables(soup)
    assert len(result) == 2
```

- [ ] **Step 10: 실패 확인**

```bash
pytest tests/test_common.py -v -k "table"
```

- [ ] **Step 11: 구현 추가**

```python
def find_target_table(soup: BeautifulSoup) -> Tag:
    """td > 20인 첫 번째 table 반환."""
    for table in soup.find_all("table"):
        if len(table.find_all("td")) > 20:
            return table
    return soup.find("table")  # fallback


def find_all_tables(soup: BeautifulSoup) -> list:
    """모든 table 리스트 반환."""
    return soup.find_all("table")
```

- [ ] **Step 12: 테스트 통과**

```bash
pytest tests/test_common.py -v -k "table"
```

### 2d. load_config

- [ ] **Step 13: 테스트 추가**

```python
import tempfile, os

def test_load_config_reads_yaml():
    from parsers.common import load_config
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    tmp.write("paths:\n  working_dir: E:/test\n")
    tmp.close()
    config = load_config(Path(tmp.name))
    assert config["paths"]["working_dir"] == "E:/test"
    os.unlink(tmp.name)

def test_load_config_default_path_exists():
    """프로젝트 루트의 config.yaml이 존재하면 로드 성공."""
    from parsers.common import load_config
    config = load_config()
    assert "paths" in config
    assert "scraper" in config
```

- [ ] **Step 14: 실패 확인**

```bash
pytest tests/test_common.py -v -k "config"
```

- [ ] **Step 15: load_config 구현**

```python
def load_config(path: Path = None) -> dict:
    """config.yaml 로드. path=None이면 프로젝트 루트 config.yaml 사용."""
    if path is None:
        path = Path(__file__).parents[1] / "config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
```

- [ ] **Step 16: 테스트 통과**

```bash
pytest tests/test_common.py -v -k "config"
```

### 2e. build_path_list

- [ ] **Step 17: 테스트 추가**

```python
def test_build_path_list_excludes_duplicated(tmp_path):
    from parsers.common import build_path_list
    d = tmp_path / "A001_2020"
    d.mkdir()
    (d / "A001_2020_good.html").touch()
    (d / "A001_2020_duplicated.html").touch()
    result = build_path_list(str(tmp_path), ["A001_2020"], "*.html")
    assert len(result) == 1
    assert "duplicated" not in result[0]

def test_build_path_list_combines_dirs(tmp_path):
    from parsers.common import build_path_list
    for name in ["A001_2020", "A001_2019"]:
        d = tmp_path / name
        d.mkdir()
        (d / f"{name}_file.html").touch()
    result = build_path_list(str(tmp_path), ["A001_2020", "A001_2019"], "*.html")
    assert len(result) == 2
```

- [ ] **Step 18: 실패 확인**

```bash
pytest tests/test_common.py -v -k "path_list"
```

- [ ] **Step 19: build_path_list 구현**

```python
def build_path_list(working_dir: str, report_dirs: list[str], pattern: str) -> list[str]:
    """
    각 report_dir에서 glob 패턴으로 파일 경로 수집.
    'duplicated' 포함 파일 제거.
    연도 필터링은 호출자 책임.
    """
    path_list = []
    for d in report_dirs:
        full_pattern = os.path.join(working_dir, d, pattern)
        path_list.extend(glob.glob(full_pattern))
    return [p for p in path_list if "duplicated" not in p]
```

- [ ] **Step 20: 테스트 통과**

```bash
pytest tests/test_common.py -v -k "path_list"
```

### 2f. preprocess_df

- [ ] **Step 21: 테스트 추가**

```python
def test_preprocess_df_creates_key_column():
    from parsers.common import preprocess_df
    # 실제 파일명 패턴:
    # reportType _ corpNo _ rcpNo _ _ _ yearEnd _ subDoc _ _ stockCode _ corpRegNo _ docName.html
    # df[2]=rcpNo(접수번호), df[5]=yearEnd(보고기간), df[6]=subDoc(문서명), df[8]=stockCode, df[10]=corpRegNo
    # 최소 11개 '_' 세그먼트 필요
    # 예: A001_CORP1234_20200301_별도_2019_(2019.12)_사업보고서_extra_STOCK1_SU_B1234_docname.html
    #       0      1         2      3     4      5            6          7      8      9     10       11
    fake_path = "A001_CORP1234_20200301_별도_2019_(2019.12)_사업보고서_extra_STOCK1_SU_B1234_docname.html"
    df = preprocess_df([fake_path])
    assert "key" in df.columns
    assert "con" in df.columns
    assert "amend" in df.columns
    assert "path" in df.columns
    # key 값 직접 검증
    expected_key = "20200301" + "사업보고서"[:10] + "S" + "B" + "(2019.12)" + "STOCK1" + "B1234"
    assert df.iloc[0]["key"] == expected_key

def test_preprocess_df_con_amend_flags():
    from parsers.common import preprocess_df
    consolidated = "A001_CORP_20200101_a_b_(2019.12)_연결사업보고서_x_STOCK_y_CORP_z.html"
    amendment   = "A001_CORP_20200101_a_b_(2019.12)_정정사업보고서_x_STOCK_y_CORP_z.html"
    df = preprocess_df([consolidated, amendment])
    assert df[df["path"].str.contains("연결")].iloc[0]["con"] == "C"
    assert df[df["path"].str.contains("정정")].iloc[0]["amend"] == "A"

def test_preprocess_df_deduplicates():
    from parsers.common import preprocess_df
    path = "A001_CORP_20200101_a_b_(2019.12)_사업보고서_x_STOCK_y_CORP_z.html"
    df = preprocess_df([path, path])
    assert len(df) == 1
```

- [ ] **Step 22: 실패 확인**

```bash
pytest tests/test_common.py -v -k "preprocess"
```

- [ ] **Step 23: preprocess_df 구현**

```python
import numpy as np

def preprocess_df(path_list: list[str]) -> pd.DataFrame:
    """
    파일명을 '_' 기준으로 분리해 DataFrame 생성.
    con, amend, key 컬럼 추가 후 key 기반 중복 제거.
    """
    path_df = pd.DataFrame(path_list, columns=["path"])
    df = pd.DataFrame([os.path.basename(p).split("_") for p in path_list])
    df["path"] = path_list

    df["con"] = np.where(df[6].str.contains("연결", na=False), "C", "S")
    df["amend"] = np.where(df[6].str.contains("정정", na=False), "A", "B")
    df["key"] = (
        df[2]
        + df[6].str.slice(stop=10)
        + df["con"]
        + df["amend"]
        + df[5]
        + df[8]
        + df[10]
    )
    df = df.drop_duplicates(subset=["key"])
    return df
```

- [ ] **Step 24: 테스트 통과**

```bash
pytest tests/test_common.py -v -k "preprocess"
```

### 2g. deduplicate_df

- [ ] **Step 25: 테스트 추가**

```python
def test_deduplicate_df_keeps_first():
    from parsers.common import deduplicate_df
    df = pd.DataFrame({
        "corp": ["A", "A", "B"],
        "year": ["2019", "2019", "2019"],
        "value": [1, 2, 3],
    })
    result = deduplicate_df(
        df,
        sort_cols=["corp", "year"],
        key_cols=["corp", "year"],
    )
    assert len(result) == 2
    assert result.iloc[0]["value"] == 1  # 정렬 후 첫 번째 유지

def test_deduplicate_df_three_consecutive():
    """3개 연속 중복 — toDrop 누적 로직 검증."""
    from parsers.common import deduplicate_df
    df = pd.DataFrame({
        "corp": ["A", "A", "A", "B"],
        "year": ["2019", "2019", "2019", "2019"],
        "value": [1, 2, 3, 4],
    })
    result = deduplicate_df(df, sort_cols=["corp", "year", "value"], key_cols=["corp", "year"])
    assert len(result) == 2
    assert result.iloc[0]["value"] == 1

def test_deduplicate_df_non_adjacent_duplicates():
    """비연속 중복 — 정렬 후 동일 키가 붙을 때만 제거."""
    from parsers.common import deduplicate_df
    df = pd.DataFrame({
        "corp": ["A", "B", "A"],  # 정렬 후 A,A,B 순
        "year": ["2019", "2019", "2019"],
        "value": [1, 3, 2],
    })
    result = deduplicate_df(df, sort_cols=["corp", "year", "value"], key_cols=["corp", "year"])
    # 정렬: A/1, A/2, B/3 → A 중복이므로 A/1만 유지, B/3 유지 → 2개
    assert len(result) == 2

def test_deduplicate_df_sort_order_affects_result():
    """sort_cols 순서에 따라 어떤 행이 유지되는지 달라짐."""
    from parsers.common import deduplicate_df
    df = pd.DataFrame({
        "corp": ["A", "A"],
        "year": ["2019", "2019"],
        "value": [10, 5],
    })
    result_asc = deduplicate_df(df, sort_cols=["corp", "year", "value"], key_cols=["corp", "year"])
    assert result_asc.iloc[0]["value"] == 5  # 오름차순 → 5가 첫 번째
```

- [ ] **Step 26: 실패 확인**

```bash
pytest tests/test_common.py -v -k "deduplicate"
```

- [ ] **Step 27: deduplicate_df 구현**

```python
def deduplicate_df(
    df: pd.DataFrame,
    sort_cols: list[str],
    key_cols: list[str],
) -> pd.DataFrame:
    """
    정렬 후 key_cols 두 컬럼 기준으로 연속 중복 제거.
    df.iloc 금지 — df.loc[idx, col] 레이블 기반 접근만 사용.
    """
    df = df.sort_values(by=sort_cols, ascending=True).reset_index(drop=True)
    df["toDrop"] = 1
    for i in range(1, len(df)):
        idx = df.index[i]
        prev_idx = df.index[i - 1]
        if (
            df.loc[idx, key_cols[0]] == df.loc[prev_idx, key_cols[0]]
            and df.loc[idx, key_cols[1]] == df.loc[prev_idx, key_cols[1]]
        ):
            df.loc[idx, "toDrop"] = df.loc[prev_idx, "toDrop"] + 1
        else:
            df.loc[idx, "toDrop"] = 1
    df = df[df["toDrop"] == 1].drop(columns=["toDrop"])
    return df
```

- [ ] **Step 28: 전체 테스트 통과**

```bash
pytest tests/test_common.py -v
```
Expected: 모든 테스트 통과

- [ ] **Step 29: 커밋**

```bash
git add parsers/common.py tests/test_common.py
git commit -m "feat: add parsers/common.py with unit tests"
```

---

## Task 3: `scraper/dart_scraper.py` — 이동 + 버그 수정 + snake_case

**Files:**
- Create: `scraper/dart_scraper.py` (Dart_Scraper.py 내용 기반)
- Modify: `app.py`

기존 `Dart_Scraper.py`의 내용을 `scraper/dart_scraper.py`로 옮기면서:
1. 함수명 PascalCase → snake_case
2. `time.delay(3)` → `time.sleep(3)` (버그 수정)
3. while 루프 → for 루프 (가능한 경우)
4. magic string 주석 추가

- [ ] **Step 1: `scraper/dart_scraper.py` 생성**

`Dart_Scraper.py`를 기반으로 아래 변경 적용:

```python
# scraper/dart_scraper.py
# -*- coding: utf-8 -*-
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import js2py
import urllib.request
from os import path
import time
from tqdm import tqdm

# 슬라이스 상수 — DART URL 구조에서 고유번호/접수번호 위치
CORP_NO_SLICE = slice(28, 36)   # href에서 감독원 고유번호 위치
RCP_NO_SLICE = slice(44, None)  # URL에서 접수번호 위치


def document_address_parser(page, start_date, end_date, report_type):
    """
    DART 공시 목록 페이지에서 문서 주소 dict 반환.
    Returns: {doc_key: doc_address}
    """
    detail_search = "http://dart.fss.or.kr/dsab007/detailSearch.ax?"
    data = {
        "currentPage": page,
        "maxResults": 15,
        "maxLinks": 10,
        "startDate": start_date,
        "endDate": end_date,
        "finalReport": "recent",
        "publicType": report_type,
    }
    company_list = requests.get(detail_search + urlencode(data))
    time.sleep(1)

    soup = BeautifulSoup(company_list.content, "html.parser")
    cells = soup.findAll("td")
    doc_list = {}

    for idx in range(1, len(cells), 6):  # td 6개마다 1건
        if idx + 1 >= len(cells):
            break
        doc_address = "http://dart.fss.or.kr" + cells[idx + 1].a["href"]
        doc_name = "".join(cells[idx + 1].a.text.split())
        report_name = doc_name.split("(")[0]
        year_end = "(" + doc_name.split("(")[1]
        doc_key = "_".join([
            report_type,
            cells[idx].a["href"][CORP_NO_SLICE],   # 감독원 고유번호
            doc_address[RCP_NO_SLICE],              # 접수번호
            report_name,
            year_end,
        ])
        doc_list[doc_key] = doc_address

    return doc_list


def sub_document_address_parser(doc_address):
    """문서 묶음에서 첨부 문서 주소 dict 반환."""
    doc_html = requests.get(doc_address)
    time.sleep(1)
    soup = BeautifulSoup(doc_html.content, "html.parser")

    sub_doc_list = soup.findAll("option")
    result = {}
    for opt in sub_doc_list[1:]:  # 첫 번째 option은 헤더
        sub_addr = "http://dart.fss.or.kr/dsaf001/main.do?" + opt["value"]
        if sub_addr == "http://dart.fss.or.kr/dsaf001/main.do?null":
            continue
        doc_name = "".join(opt.text.split())
        key = "_".join([
            sub_addr[44:58],                        # 접수번호 앞부분
            "_".join([doc_name[:10], doc_name[10:]])
        ])
        result[key] = sub_addr
    return result


def html_address_parser(sub_doc_address):
    """첨부 문서에서 개별 HTML 주소 dict 반환."""
    doc_html = requests.get(sub_doc_address)
    time.sleep(1)
    soup = BeautifulSoup(doc_html.content, "html.parser")

    j_scripts = "".join(tag.text for tag in soup.findAll("script"))
    j_scripts = j_scripts.split("winCorpInfo');")[1]
    j_scripts = j_scripts.split("//js tree")[0]

    context = js2py.EvalJs(enable_require=True)
    context.execute(j_scripts)

    dict_list = list(context.treeData)
    for item in dict_list:
        item.pop("children", None)

    addr_list = {}
    for item in dict_list:
        doc_name = "".join(item["text"].split())
        for key in ["id", "tocNo", "text"]:
            item.pop(key, None)
        addr_list[doc_name] = "http://dart.fss.or.kr/report/viewer.do?" + urlencode(item)
    return addr_list


def get_html(html_address, doc_key):
    """HTML 파일 다운로드. 실패 시 재시도."""
    try:
        urllib.request.urlretrieve(html_address, doc_key)
    except FileNotFoundError:
        print("Error Occurred at", html_address)
        time.sleep(3)  # 버그 수정: time.delay → time.sleep
        get_html(html_address, doc_key)


def dart_scraper(report_type, current_page, start_date, end_date, delay=1):
    """한 페이지의 모든 문서를 스크랩. 처리 문서 수 반환."""
    doc_address_dict = document_address_parser(current_page, start_date, end_date, report_type)
    docs_in_page = list(doc_address_dict.items())

    for doc_key, doc_address in tqdm(docs_in_page, desc="docs in this page"):
        sub_docs = list(sub_document_address_parser(doc_address).items())
        for sub_key, sub_addr in tqdm(sub_docs, desc="subdocs", leave=False):
            html_docs = list(html_address_parser(sub_addr).items())
            for html_name, html_addr in tqdm(html_docs, desc="htmls", leave=False):
                file_key = "_".join([doc_key, sub_key, html_name, ".html"])
                if not path.exists(file_key):
                    get_html(html_addr, file_key)
                    time.sleep(delay)

    return len(docs_in_page)
```

- [ ] **Step 2: `app.py` 수정 — import 경로 변경 + 재귀→while**

```python
# app.py
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.dart_scraper import dart_scraper
from os import chdir
import time
from urllib.error import URLError
from requests import exceptions
import ssl


def app(start_page, query):
    i = start_page
    while True:
        try:
            print("Current page:", i)
            result = dart_scraper(
                query["reportType"], i, query["start"], query["end"]
            )
            i += 1
            if result < 15:  # 마지막 페이지
                break
        except (
            FileNotFoundError,
            URLError,
            ConnectionResetError,
            ConnectionAbortedError,
            ssl.SSLEOFError,
            exceptions.SSLError,
        ) as e:
            print("Wait 300s. Error:", e)
            time.sleep(300)
            # i 유지 — 에러 발생 페이지부터 재시도


chdir(input("Enter location (C:\\F001_2020): "))
query = {
    "reportType": str(input("Enter reportType (A001, F001): ")),
    "start": input("Registered from (20200101): "),
    "end": input("Registered to (20201231): "),
}
i = int(input("loop start(resume) from page Number: "))
app(i, query)
```

- [ ] **Step 3: 커밋**

```bash
git add scraper/dart_scraper.py app.py
git commit -m "feat: migrate dart_scraper to package, fix bugs, snake_case"
```

---

## Task 4: `parsers/d1_business_report_cover.py` — 첫 번째 파서 마이그레이션 (패턴 확립)

**Files:**
- Create: `parsers/d1_business_report_cover.py`

D-1은 `find_all_tables` 사용. `ParsingTime`이 있지만 D-1의 메인 로직은 `<tr>` 텍스트 검색이므로 `matrix_generator` 미사용. 이 파서를 패턴으로 삼아 이후 파서들을 마이그레이션한다.

- [ ] **Step 1: 원본 D-1 내용 확인하고 `parsers/d1_business_report_cover.py` 작성**

원본 `(D-1) businessReportCover`의 로직을 유지하면서:
- 상단에 `sys.path` 추가
- `os.chdir` 제거 → `load_config()`로 경로 읽기
- 하드코딩된 경로 제거
- 하드코딩된 연도 리스트(`".\A001_2017\\"` 등) → `build_path_list()` + 연도 필터
- `preprocess_df()`, `deduplicate_df()` 사용
- 함수명 snake_case로 변경
- `container(...)` 버그 수정 → `container.append(...)`
- 출력 경로 → `config["paths"]["output_dir"]`

```python
# parsers/d1_business_report_cover.py
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from bs4 import BeautifulSoup
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
    find_all_tables, matrix_generator, col_span_count, row_span_count,
)

# --- 파서 고유 함수 ---

def parsing_time(matrix, is_comparative, table_length, file, report):
    if is_comparative:
        table_length = int(table_length / 2)
        return [
            f"{file}_{matrix[report][1]}_{matrix[1][2+2*i]}_{matrix[report][2+2*i].replace('-','0').replace(',','')}\n"
            for i in range(table_length)
        ]
    else:
        return [
            f"{file}_{matrix[report][1]}_{matrix[1][2+i]}_{matrix[report][2+i].replace('-','0').replace(',','')}\n"
            for i in range(int(table_length))
        ]


def indexing(matrix):
    keywords = ["투입 인원수", "분ㆍ반기검토", "감사", "합계"]
    container = []
    for i, row in enumerate(matrix):
        for kw in keywords:
            try:
                row[0:2].index(kw)
                container.append(i)
            except ValueError:
                pass
    return container


# --- 메인 처리 ---

config = load_config()
WORKING_DIR = config["paths"]["working_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]

path_list = build_path_list(WORKING_DIR, REPORT_DIRS, "*사업보고서_사업보고서*.*")
# 연도 필터: D-1은 2017~2019
path_list = (
    [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

df = preprocess_df(path_list)
path_list_out = df["path"].tolist()

result = []
count = 0

for file in path_list_out:
    with open(file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    container = []
    for row in soup.find_all("tr"):
        j = "".join(row.text.replace("\n", "").split())
        if j.count("부터") - j.count("면제") - j.count("제외") == 1:
            container.append(j)
        elif j.count("까지") == 1:
            container.append(j)
        elif j.count("회사명") == 1:
            container.append(j)
        elif j.count("법인유형") == 1:
            container.append(j)

    result.append("_".join(container))
    count += 1
    print(count, end="\n")

df["businessReportCover"] = result
df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")

df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[3, 8],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data03.output.csv"), sep="\t")
```

- [ ] **Step 2: 커밋**

```bash
git add "parsers/d1_business_report_cover.py"
git commit -m "feat: migrate D-1 businessReportCover parser"
```

---

## Task 5: D-2, D-3 파서 마이그레이션

**Files:**
- Create: `parsers/d2_1_audit_cover_period.py`
- Create: `parsers/d2_2_audit_cover_auditor.py`
- Create: `parsers/d3_1_audit_firm.py`
- Create: `parsers/d3_2_audit_opinion.py`
- Create: `parsers/d3_3_audit_date.py`
- Create: `parsers/d3_4_audit_gaap.py`

D-1 패턴을 따라 각 파서를 마이그레이션한다. 변경 사항은 Task 4와 동일:
- sys.path 추가, os.chdir 제거, config 사용, snake_case, container 버그 수정

주요 차이점:
- D-2-1, D-2-2: `find_all_tables` 사용 (D-2-1의 원본과 동일)
- D-3-1: `find_all_tables` 사용
- D-3-2, D-3-3, D-3-4: 원본 코드 확인 후 적절한 함수 사용

- [ ] **Step 1: 각 원본 파일 내용 확인 후 마이그레이션**

원본 `(D-2-1)`, `(D-2-2)`, `(D-3-1)` ~ `(D-3-4)` 각각을 읽고,
Task 4의 패턴에 따라 `parsers/d2_*.py`, `parsers/d3_*.py`로 작성.

각 파서에서 확인할 사항:
- glob 패턴 (어떤 파일을 대상으로 하는가)
- 연도 필터 범위
- 출력 CSV 파일명
- `ParsingTime` 등 고유 함수 존재 여부

- [ ] **Step 2: 커밋**

```bash
git add parsers/d2_*.py parsers/d3_*.py
git commit -m "feat: migrate D-2, D-3 audit cover/report parsers"
```

---

## Task 6: D-4, D-5, D-6 파서 마이그레이션

**Files:**
- Create: `parsers/d4_1_time_information.py`
- Create: `parsers/d4_2_audit_activity.py`
- Create: `parsers/d4_3_audit_activity_communication.py`
- Create: `parsers/d5_1_total_asset.py`
- Create: `parsers/d5_2_net_income.py`
- Create: `parsers/d5_3_inv_rec.py`
- Create: `parsers/d6_1_ic_review.py`

D-4-1, D-5-1, D-5-2, D-5-3, D-6-1: `find_target_table` (단일 table, td > 20) 사용.
D-4-2: `working_dir`이 `C:\data\` (spec의 `governance_dir`과 동일 경로) → `config["paths"]["governance_dir"]` 사용.

- [ ] **Step 1: 각 원본 파일 내용 확인 후 마이그레이션**

Task 4 패턴 동일. D-4-2의 경우 `working_dir` 대신 `governance_dir` 키 사용:

```python
# parsers/d4_2_audit_activity.py 상단
WORKING_DIR = config["paths"]["governance_dir"]  # C:/data (D-4-2 전용)
```

- [ ] **Step 2: 커밋**

```bash
git add parsers/d4_*.py parsers/d5_*.py parsers/d6_1_ic_review.py
git commit -m "feat: migrate D-4, D-5, D-6 parsers"
```

---

## Task 7: D-7-1 거버넌스 파서 마이그레이션 (OCR)

**Files:**
- Create: `parsers/d7_1_governance.py`

D-7-1은 OCR 의존성(`pytesseract`, `skimage`) 사용. 나머지 변경 사항은 동일.
`working_dir` → `config["paths"]["governance_dir"]`.

- [ ] **Step 1: 원본 `(D-7-1) extractGovernance` 읽고 마이그레이션**

Task 4 패턴 적용. `find_all_tables` 사용.

- [ ] **Step 2: 커밋**

```bash
git add parsers/d7_1_governance.py
git commit -m "feat: migrate D-7-1 governance parser (OCR)"
```

---

## Task 8: `merge/` E-series 마이그레이션

**Files:**
- Create: `merge/e1_merge_period.py`
- Create: `merge/e2_merge_auditor.py`
- Create: `merge/e3_merge_reportdate.py`
- Create: `merge/e4_merge_financials.py`
- Create: `merge/e5_audit_committee.py`

E-series는 CSV 병합 스크립트. `os.chdir` 제거 → `load_config()` 로 경로 읽기. `industry.xlsx` 경로도 config 기반으로 변경.

- [ ] **Step 1: E-series 각 원본 읽기**

원본 `(E-1)` ~ `(E-5)` 파일 내용 확인.

- [ ] **Step 2: `merge/e1_merge_period.py` 작성 (패턴 확립)**

```python
# merge/e1_merge_period.py
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import pandas as pd
from parsers.common import load_config

config = load_config()
OUTPUT_DIR = config["paths"]["output_dir"]
DATA_DIR = config["paths"]["data_dir"]

# --- 이하 원본 E-1 로직. os.chdir 제거, 경로는 OUTPUT_DIR 기준 ---

df1 = pd.read_csv(os.path.join(OUTPUT_DIR, "wp01.data06.output.csv"), header=[0, 1], sep="\t")
df1.columns = df1.columns.map("_".join)
df1 = df1.drop([0])
df1 = df1.rename(columns={"B_C": "key"})

df2 = pd.read_csv(os.path.join(OUTPUT_DIR, "wp01.data02.output.csv"), sep="\t")
df2 = df2.loc[:, ~df2.columns.str.contains("^Unnamed")]
df2["subKey"] = df2["5"] + df2["10"]

df3 = pd.read_csv(os.path.join(OUTPUT_DIR, "wp01.data03.output.csv"), sep="\t")
df3 = df3.loc[:, ~df3.columns.str.contains("^Unnamed")]
df3["subKey"] = df3["5"] + df3["10"]

df = pd.merge(df2, df3[["subKey", "businessReportCover"]], how="left", on="subKey")
df = pd.merge(df, df1[["key", "감사_합계"]], how="left", on="key")

df = df[(df["5"] == "(2017.12)") | (df["5"] == "(2018.12)") | (df["5"] == "(2019.12)")]

df_ind = pd.read_excel(os.path.join(DATA_DIR, "industry.xlsx"), dtype={"KSIC": str}, sheet_name="data")
df = df.rename(columns={"11": "INDUSTRY"})
df = pd.merge(df, df_ind, on="INDUSTRY", how="left")
df = df[df["FIN"] == 0]
df = df[df["감사_합계"] >= 100]

df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data.period.csv"), sep="\t")
```

- [ ] **Step 3: 나머지 E-series 원본 읽고 동일 패턴으로 작성**

- [ ] **Step 4: 커밋**

```bash
git add merge/
git commit -m "feat: migrate E-series merge scripts"
```

---

## Task 9: 구버전 파일 삭제 + 최종 정리

**Files:**
- Delete: `Dart_Scraper.py` (scraper/dart_scraper.py로 대체됨)
- Delete: `(D-1) businessReportCover` 등 원본 D/E 파일들

- [ ] **Step 1: 원본 파일 삭제**

```bash
git rm "Dart_Scraper.py"
git rm "(D-1) businessReportCover" "(D-2-1) auditReportCoverCurrentPeriod" \
       "(D-2-2) auditReportCoverAuditor" "(D-3-1) auditReportFirm" \
       "(D-3-2) auditReportOpinion" "(D-3-3) auditReportDate" \
       "(D-3-4) auditReportGAAP" "(D-4-1) extract_time_information" \
       "(D-4-2) auditActivity" "(D-4-3) auditActivity_communication" \
       "(D-5-1) extract_totalAsset" "(D-5-2) extract_netIncome" \
       "(D-5-3) extract_invRec" "(D-6-1) icReview" "(D-7-1) extractGovernance"
git rm "(E-1) mergeCSV_period" "(E-2) mergeCSV_auditor" "(E-3) mergeCSV_reportdate" \
       "(E-4) mergeCSV_financials" "(E-5) auditCommittee"
git rm "(D-2-2) data01.auditor.txt"  # 데이터 파일도 정리
```

- [ ] **Step 2: 전체 테스트 최종 확인**

```bash
pytest tests/ -v
```
Expected: 모든 테스트 통과

- [ ] **Step 3: 최종 커밋**

```bash
git commit -m "chore: remove legacy script files after migration"
```

---

## 완료 체크리스트

- [ ] `config.yaml` 존재하고 경로 설정됨
- [ ] `requirements.txt` 존재
- [ ] `parsers/common.py` 모든 테스트 통과
- [ ] `scraper/dart_scraper.py` — `time.delay` 버그 수정됨
- [ ] `app.py` — 재귀 호출 → while 루프
- [ ] D-1 ~ D-7-1 각 파서 — sys.path 추가, config 사용, `container()` 버그 수정
- [ ] E-1 ~ E-5 병합 스크립트 — sys.path 추가, config 사용
- [ ] 구버전 파일 삭제됨
- [ ] `(A) scraper_refactoring.py` → `archive/`로 이동됨
