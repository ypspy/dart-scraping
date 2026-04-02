# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import glob
import yaml
import pandas as pd
import numpy as np

def col_span_count(soup) -> int:
    """Return td/th colspan value, or 1 if absent."""
    return int(soup.get("colspan", 1))


def row_span_count(soup) -> int:
    """Return td/th rowspan value, or 1 if absent."""
    return int(soup.get("rowspan", 1))


def matrix_generator(table) -> list:
    """Convert HTML table to 2D list, handling rowspan and colspan."""
    rows = table.find_all("tr")
    row_count = len(rows)
    if row_count == 0:
        return []

    # Estimate column count
    col_count = sum(col_span_count(c) for c in rows[0].find_all(["td", "th"]))

    # Initialize grid
    grid = [[None] * col_count for _ in range(row_count)]

    for r_idx, row in enumerate(rows):
        cells = row.find_all(["td", "th"])
        c_fill = 0
        for cell in cells:
            # skip already-filled slots
            while c_fill < col_count and grid[r_idx][c_fill] is not None:
                c_fill += 1
            if c_fill >= col_count:
                break
            text = cell.get_text(strip=True)
            rspan = row_span_count(cell)
            cspan = col_span_count(cell)
            for dr in range(rspan):
                for dc in range(cspan):
                    r2 = r_idx + dr
                    c2 = c_fill + dc
                    if r2 < row_count and c2 < col_count:
                        grid[r2][c2] = text
            c_fill += cspan

    # Replace None with empty string
    return [[c if c is not None else "" for c in row] for row in grid]


def find_target_table(soup) -> object:
    """Return the first table with more than 20 td elements."""
    for table in soup.find_all("table"):
        if len(table.find_all("td")) > 20:
            return table
    return None


def find_all_tables(soup) -> list:
    """Return all tables as a list."""
    return list(soup.find_all("table"))


def load_config(path: Path = None) -> dict:
    """Load config.yaml. Defaults to project root if path is None."""
    if path is None:
        path = Path(__file__).parents[1] / "config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_path_list(working_dir: str, report_dirs: list, pattern: str) -> list:
    """Collect file paths from each report_dir matching pattern, excluding 'duplicated' files."""
    path_list = []
    for report_dir in report_dirs:
        glob_pattern = str(Path(working_dir) / report_dir / pattern)
        path_list.extend(glob.glob(glob_pattern))
    return [p for p in path_list if "duplicated" not in p]


def preprocess_df(path_list: list) -> pd.DataFrame:
    """
    Parse filenames (underscore-separated, extension stripped) into DataFrame.
    Adds path, con, amend, key columns. Removes exact key duplicates.
    key = df[2] + df[6].str.slice(stop=10) + con + amend + df[5] + df[8] + df[10]
    """
    basenames_no_ext = [Path(p).stem for p in path_list]
    df = pd.DataFrame([n.split("_") for n in basenames_no_ext])
    df["path"] = path_list
    df["con"] = np.where(df[6].str.contains("연결", na=False), "C", "S")
    df["amend"] = np.where(df[6].str.contains("정정", na=False), "A", "B")
    df["key"] = (
        df[2].astype(str)
        + df[6].str.slice(stop=10)
        + df["con"]
        + df["amend"]
        + df[5].astype(str)
        + df[8].astype(str)
        + df[10].astype(str)
    )
    df = df.drop_duplicates(subset=["key"])
    return df


def deduplicate_df(df: pd.DataFrame, sort_cols: list, key_cols: list) -> pd.DataFrame:
    """
    Sort by sort_cols, apply toDrop logic using label-based indexing.
    Keep only rows where toDrop == 1 (first occurrence of each consecutive key group).
    """
    df = df.sort_values(by=sort_cols).reset_index(drop=True)
    df["toDrop"] = 1
    for i in range(1, len(df)):
        if (df.loc[i, key_cols[0]] == df.loc[i - 1, key_cols[0]]
                and df.loc[i, key_cols[1]] == df.loc[i - 1, key_cols[1]]):
            df.loc[i, "toDrop"] = df.loc[i - 1, "toDrop"] + 1
        else:
            df.loc[i, "toDrop"] = 1
    df = df[df["toDrop"] == 1].drop(columns=["toDrop"])
    return df
