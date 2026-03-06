# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import os
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union, Literal

import pandas as pd

from langchain_core.documents import Document
from langchain_community.document_loaders import JSONLoader, DataFrameLoader


class JSONCustomLoader(JSONLoader):
    """Load a `JSON` file using a `jq` schema and handle custom metadata extraction."""

    def __init__(
        self,
        file_path: Union[str, Path],
        category: str,
        index: int | str,
        jq_schema: str,
        content_key: Optional[str] = None,
        is_content_key_jq_parsable: Optional[bool] = False,
        metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
        text_content: bool = True,
        json_lines: bool = False,
        metadata_keys: Optional[
            List[str]
        ] = None,  # List of keys to include in metadata
    ):
        """Initialize the JSONCustomLoader.

        Args:
            file_path (Union[str, Path]): The path to the JSON or JSON Lines file.
            jq_schema (str): The jq schema to use to extract the data or text from the JSON.
            content_key (str): The key to use to extract the content from the JSON if the jq_schema results to a list of objects (dict).
            index (int | str): Index of document
            is_content_key_jq_parsable (bool): A flag to determine if content_key is parsable by jq or not.
            metadata_func (Callable[Dict, Dict]): A function that takes in the JSON object extracted by the jq_schema and the default metadata and returns a dict of the updated metadata.
            text_content (bool): Boolean flag to indicate whether the content is in string format, default to True.
            json_lines (bool): Boolean flag to indicate whether the input is in JSON Lines format.
            metadata_keys (List[str]): List of keys to include in the metadata.
        """
        try:
            import jq  # noqa:F401

            self.jq = jq
        except ImportError:
            raise ImportError(
                "jq package not found, please install it with `pip install jq`"
            )

        self.file_path = Path(file_path).resolve()
        self._jq_schema = jq.compile(jq_schema)
        self._is_content_key_jq_parsable = is_content_key_jq_parsable
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._text_content = text_content
        self._json_lines = json_lines
        self.metadata_keys = (
            metadata_keys or []
        )  # Initialize with an empty list if None
        self.category = category
        self.index = index

    def lazy_load(self) -> Iterator[Document]:
        """Load and yield documents from the JSON file."""
        if self._json_lines:
            with self.file_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        metadata = {
                            "source": os.path.basename(self.file_path),
                            "index": self.index,
                            "category": self.category,
                        }

                        # Extract specified keys for metadata
                        for key in self.metadata_keys:
                            if key in data:
                                metadata[key] = data[key]

                        # Convert remaining data to string
                        text = json.dumps(data, ensure_ascii=False, indent=4)

                        yield Document(
                            page_content=text,
                            metadata=metadata,
                        )
        else:
            with self.file_path.open(encoding="utf-8") as f:
                data = json.load(f)

                metadata = {
                    "source": os.path.basename(self.file_path),
                    "index": self.index,
                    "category": self.category,
                }

                # Extract specified keys for metadata
                for key in self.metadata_keys:
                    if key in data:
                        metadata[key] = data[key]

                # Convert remaining data to string
                page_content = json.dumps(data, ensure_ascii=False, indent=4)

                yield Document(
                    page_content=page_content,
                    metadata=metadata,
                )


class CustomDataFrameLoader(DataFrameLoader):
    def __init__(
        self,
        data_frame: Any,
        page_content_column: str = "text",
        engine: Literal["pandas", "modin"] = "pandas",
        data_type: str = "curriculum",
    ):
        """Initialize with dataframe object.

        Args:
            data_frame: Pandas DataFrame object.
            page_content_column: Name of the column containing the page content.
              Defaults to "text".
        """
        try:
            if engine == "pandas":
                import pandas as pd
            elif engine == "modin":
                import modin.pandas as pd
            else:
                raise ValueError(
                    f"Unsupported engine {engine}. Must be one of 'pandas', or 'modin'."
                )
        except ImportError as e:
            raise ImportError(
                "Unable to import pandas, please install with `pip install pandas`."
            ) from e

        if not isinstance(data_frame, pd.DataFrame):
            raise ValueError(
                f"Expected data_frame to be a pd.DataFrame, got {type(data_frame)}"
            )
        super().__init__(data_frame, page_content_column=page_content_column)
        self.data_type = data_type.lower()

    def preprocess_csv(self):
        if "Unnamed: 0" in self.data_frame.columns:
            self.data_frame = self.data_frame.drop(columns=["Unnamed: 0"])
        if self.data_type == "problem":

            def make_content(row):
                subject = row.get("subject", "")
                if subject == "영어":
                    return f"대단원:{row['section']}\n중단원:{row['unit']}\n문항:{row['problem']}"
                else:
                    return f"중단원:{row['unit']}\n문항:{row['problem']}"

            self.data_frame["content"] = self.data_frame.apply(make_content, axis=1)

        elif self.data_type == "curriculum":
            # course_2015.csv or course_2022.csv
            self.data_frame["content"] = self.data_frame.apply(
                lambda row: f"대단원:{row['section']}\n중단원:{row['unit']}\n주제:{row['topic']}",
                axis=1,
            )
        elif self.data_type == "contents":
            # contents_fig_math.parquet
            self.data_frame["content"] = self.data_frame.apply(
                lambda row: f"개념:{row['concept']}\n설명:{row['description']}",
                axis=1,
            )
        else:
            # TODO: add embedding logic of memory
            raise ValueError(f"Data type '{self.data_type}' is not implemented.")

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load records from dataframe and customize processing."""
        self.preprocess_csv()
        for _, row in self.data_frame.iterrows():
            text = row[self.page_content_column]
            metadata = row.to_dict()
            metadata.pop(self.page_content_column)
            metadata = {k: ("" if pd.isna(v) else str(v)) for k, v in metadata.items()}
            yield Document(page_content=text, metadata=metadata)
