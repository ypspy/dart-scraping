import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import pandas as pd
from bs4 import BeautifulSoup
from parsers.common import (
    col_span_count, row_span_count, matrix_generator,
    find_target_table, find_all_tables,
    load_config, build_path_list, preprocess_df, deduplicate_df,
)


# --- col_span_count ---

def test_col_span_count_with_colspan():
    soup = BeautifulSoup('<td colspan="3">x</td>', "lxml")
    tag = soup.find("td")
    assert col_span_count(tag) == 3

def test_col_span_count_without_colspan():
    soup = BeautifulSoup('<td>x</td>', "lxml")
    tag = soup.find("td")
    assert col_span_count(tag) == 1


# --- row_span_count ---

def test_row_span_count_with_rowspan():
    soup = BeautifulSoup('<td rowspan="2">x</td>', "lxml")
    tag = soup.find("td")
    assert row_span_count(tag) == 2

def test_row_span_count_without_rowspan():
    soup = BeautifulSoup('<td>x</td>', "lxml")
    tag = soup.find("td")
    assert row_span_count(tag) == 1


# --- matrix_generator ---

def test_matrix_generator_simple():
    html = """
    <table>
      <tr><td>A</td><td>B</td></tr>
      <tr><td>C</td><td>D</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    result = matrix_generator(table)
    assert result == [["A", "B"], ["C", "D"]]

def test_matrix_generator_rowspan_and_colspan():
    html = """
    <table>
      <tr><td rowspan="2">A</td><td colspan="2">B</td></tr>
      <tr><td>C</td><td>D</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    result = matrix_generator(table)
    assert result[0] == ["A", "B", "B"]
    assert result[1] == ["A", "C", "D"]


# --- find_target_table ---

def test_find_target_table_returns_table_with_most_tds():
    small_tds = "".join("<td>x</td>" for _ in range(5))
    large_tds = "".join("<td>x</td>" for _ in range(25))
    html = f"<html><body><table><tr>{small_tds}</tr></table><table><tr>{large_tds}</tr></table></body></html>"
    soup = BeautifulSoup(html, "lxml")
    result = find_target_table(soup)
    assert result is not None
    assert len(result.find_all("td")) == 25

def test_find_target_table_returns_none_when_no_large_table():
    small_tds = "".join("<td>x</td>" for _ in range(5))
    html = f"<html><body><table><tr>{small_tds}</tr></table></body></html>"
    soup = BeautifulSoup(html, "lxml")
    result = find_target_table(soup)
    assert result is None

def test_matrix_generator_empty_table():
    html = "<table></table>"
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    result = matrix_generator(table)
    assert result == []


# --- find_all_tables ---

def test_find_all_tables_returns_list():
    html = "<html><body><table><tr><td>A</td></tr></table><table><tr><td>B</td></tr></table></body></html>"
    soup = BeautifulSoup(html, "lxml")
    result = find_all_tables(soup)
    assert isinstance(result, list)
    assert len(result) == 2


# --- load_config ---

def test_load_config_returns_dict(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("paths:\n  working_dir: /tmp\n")
    result = load_config(cfg)
    assert isinstance(result, dict)
    assert result["paths"]["working_dir"] == "/tmp"


# --- build_path_list ---

def test_build_path_list_excludes_duplicated(tmp_path):
    d = tmp_path / "A001_2017"
    d.mkdir()
    (d / "file_normal.html").write_text("x")
    (d / "file_duplicated.html").write_text("x")
    result = build_path_list(str(tmp_path), ["A001_2017"], "*.html")
    assert any("normal" in p for p in result)
    assert not any("duplicated" in p for p in result)


# --- preprocess_df ---

def test_preprocess_df_creates_key_column(tmp_path):
    # filename parts (underscore-split after removing extension):
    # 0=x, 1=x, 2=RCPNO, 3=x, 4=x, 5=PERIOD, 6=2021.01.01CONNECTEDORIGINAL, 7=x, 8=STOCKCD, 9=x, 10=CORPNO
    filename = "x_x_RCPNO_x_x_PERIOD_2021.01.01CONNECTEDORIGINAL_x_STOCKCD_x_CORPNO.html"
    f = tmp_path / filename
    f.write_text("x")
    df = preprocess_df([str(f)])
    # "CONNECTEDORIGINAL" does not contain Korean "연결" or "정정" → con="S", amend="B"
    expected_key = "RCPNO" + "2021.01.01" + "S" + "B" + "PERIOD" + "STOCKCD" + "CORPNO"
    assert df["key"].iloc[0] == expected_key


# --- deduplicate_df ---

def test_deduplicate_df_keeps_first_of_duplicates():
    df = pd.DataFrame([
        ("A", "2020", "v1"),
        ("A", "2020", "v2"),
    ], columns=["corp", "period", "val"])
    result = deduplicate_df(df, sort_cols=["period", "corp"], key_cols=["corp", "period"])
    assert len(result) == 1
    assert result.iloc[0]["val"] == "v1"

def test_deduplicate_df_keeps_non_duplicates():
    df = pd.DataFrame([
        ("A", "2020", "v1"),
        ("B", "2020", "v2"),
    ], columns=["corp", "period", "val"])
    result = deduplicate_df(df, sort_cols=["period", "corp"], key_cols=["corp", "period"])
    assert len(result) == 2

def test_deduplicate_df_three_consecutive_same_key():
    df = pd.DataFrame([
        ("A", "2020", "v1"),
        ("A", "2020", "v2"),
        ("A", "2020", "v3"),
    ], columns=["corp", "period", "val"])
    result = deduplicate_df(df, sort_cols=["period", "corp"], key_cols=["corp", "period"])
    assert len(result) == 1

def test_deduplicate_df_non_adjacent_duplicates():
    df = pd.DataFrame([
        ("A", "2020", "v1"),
        ("B", "2020", "v2"),
        ("A", "2020", "v3"),
    ], columns=["corp", "period", "val"])
    # sort_cols=["corp", "period"] → A/2020/v1, A/2020/v3, B/2020/v2
    result = deduplicate_df(df, sort_cols=["corp", "period"], key_cols=["corp", "period"])
    assert len(result) == 2
    corps = set(result["corp"].tolist())
    assert corps == {"A", "B"}
