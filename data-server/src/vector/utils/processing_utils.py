# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import pandas as pd


def check_index_path_keywords(index_name: str) -> str:
    keywords = ["problem", "curriculum", "contents", "memory"]
    for keyword in keywords:
        if keyword in index_name.lower():
            return keyword
    return None  # Return None if no keyword is found


def load_dataframe(file_path: str, docs_type: str) -> pd.DataFrame:
    """Load a DataFrame from a file based on its type."""
    if docs_type == "csv":
        return pd.read_csv(file_path, encoding="utf-8")
    elif docs_type == "parquet":
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported document type: {docs_type}")
