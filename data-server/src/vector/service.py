# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import weaviate
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5

from config.config import db_config
from vector.utils.embedding_module import CustomEmbedding, EmbeddingType
from vector.utils.processing_utils import check_index_path_keywords, load_dataframe
from vector.utils.rag_utils import CustomDataFrameLoader, JSONCustomLoader
from vector.utils.weaviate_module import CustomWeaviateVectorStore


class VectorDBManager:
    """
    VectorDB Schedular

    Reference
    https://python.langchain.com/docs/integrations/vectorstores/weaviate/
    """

    def __init__(self, logger):
        """
        Initialize the VectorDBBuilder with model and device settings.
        """
        self.logger = logger
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "run",
                    "class": "VectorDB",
                    "description": "vectorDB builder with embedding model",
                }
            )
        )
        self.data_type = None
        self.index_name = None
        self.weaviate_client = weaviate.connect_to_local(
            host=db_config.WEAVIATE_HOST, 
            port=db_config.WEAVIATE_PORT,
        )
        self.embedding = CustomEmbedding(embedding_type=EmbeddingType.CLOVA_STUDIO)

    def get(self, index_name: str, ids: str | list):
        """Retrieve items corresponding to the given id or list of ids."""
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "get",
                    "class": "VectorDB",
                    "description": f"get info from {index_name}: {ids}",
                },
                ensure_ascii=False,
            )
        )
        collection = self.weaviate_client.collections.get(index_name)

        if isinstance(ids, str):
            response = collection.query.fetch_objects(filters=Filter.by_id().equal(ids))
            responses = response.objects
        else:
            responses = []
            for id in ids:
                response = collection.query.fetch_objects(
                    filters=Filter.by_id().equal(id)
                )
                responses += response.objects
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "get",
                    "class": "VectorDB",
                    "description": f"get results: {responses}",
                },
                ensure_ascii=False,
            )
        )

        return responses

    def search(self, index_name: str, retrieve_info: dict):
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "retrieve",
                    "class": "VectorDB",
                    "description": f"retrieve info: {retrieve_info}",
                },
                ensure_ascii=False,
            )
        )
        # query check
        query = retrieve_info.get("query", "")
        if not query:
            raise ValueError("Query string is required in retrieve_info")

        self.index_name = index_name
        db = CustomWeaviateVectorStore(
            client=self.weaviate_client,
            index_name=self.index_name,
            text_key="text",
            embedding=self.embedding,
        )

        # optional filter
        where_filter = None
        filter_info = retrieve_info.get("filter")

        if filter_info:
            where_filter = []
            if isinstance(filter_info, dict):
                filter_info = [filter_info]

            for _filter_info in filter_info:
                prop = _filter_info.get("property")
                val = _filter_info.get("value")
                if prop and val:
                    where_filter.append(Filter.by_property(prop).equal(val))

            where_filter = Filter.all_of(where_filter)  # AND

        # search type
        k = retrieve_info.get("k", 3)
        search_type = retrieve_info.get("search_type", "similarity").lower()
        alpha = retrieve_info.get("alpha", 0.7)
        if search_type == "mmr":
            docs = db.max_marginal_relevance_search(query, k=k, filters=where_filter)
        elif search_type == "similarity":
            docs = db.similarity_search_with_score(
                query, k=k, alpha=alpha, filters=where_filter
            )
        else:
            docs = db.similarity_search_with_score(
                query, k=k, alpha=alpha, filters=where_filter
            )
            self.logger.debug(
                json.dumps(
                    {
                        "log_type": "retrieve",
                        "class": "VectorDB",
                        "description": f"Search type {search_type} is not supported. Falling back to 'similarity'.",
                    },
                    ensure_ascii=False,
                )
            )
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "retrieve",
                    "class": "VectorDB",
                    "description": f"retrieve results: {docs}",
                },
                ensure_ascii=False,
            )
        )
        return docs

    def load_documents(self, data_paths: List[Dict[str, Optional[List[str]]]]):
        """
        Load documents from various JSON files.

        Args:
            data_paths (List[Dict]): A list of dictionaries with 'file_path', 'jq_schema',
                                      'metadata_keys', and 'json_lines' as keys.
        """
        documents = []
        for data_path in data_paths:
            file_path = data_path["file_path"]
            docs_type = data_path.get("docs_type", "csv")

            if docs_type in ["csv", "parquet"]:
                df = load_dataframe(file_path, docs_type)
                loader = CustomDataFrameLoader(
                    data_frame=df,
                    page_content_column="content",
                    engine="pandas",
                    data_type=self.data_type,
                )

            elif docs_type == "json":
                jq_schema = data_path.get("jq_schema", ".")
                content_key = data_path.get("content_key", None)
                category = data_path.get("category", None)
                index = data_path.get("index", None)
                metadata_keys = data_path.get("metadata_keys", [])
                json_lines = data_path.get("json_lines", False)
                loader = JSONCustomLoader(
                    file_path=file_path,
                    category=category,
                    index=index,
                    jq_schema=jq_schema,
                    content_key=content_key,
                    text_content=False,
                    json_lines=json_lines,
                    metadata_keys=metadata_keys,
                )

            loaded_docs = list(loader.lazy_load())
            self.logger.debug(
                json.dumps(
                    {
                        "log_type": "run",
                        "class": "VectorDB",
                        "description": f"load {len(loaded_docs)} documents from {file_path}",
                    },
                    ensure_ascii=False,
                )
            )
            documents.extend(loaded_docs)
        return documents

    def build_weaviate_index(self, documents):
        """
        Build the weaviate index using the loaded documents.
        """
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "init",
                    "class": "VectorDB",
                    "description": f"weaviate index",
                },
                ensure_ascii=False,
            )
        )

        ids = [doc.metadata["index"] for doc in documents]

        db = CustomWeaviateVectorStore.from_documents(
            documents,
            self.embedding.embedding_model_huggingface,
            ids=ids,  # uuid
            client=self.weaviate_client,
            index_name=self.index_name,
        )
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"weaviate index",
                },
                ensure_ascii=False,
            )
        )
        return db

    def run(
        self,
        index_name: str,
        data_paths: List[Dict[str, Optional[List[str]]]],
    ):
        """
        Run the entire pipeline: load documents, build index, and save it.

        Args:
            index_name (str): Name of the Weaviate collection to store or retrieve documents.
            data_paths (List[Dict]): A list of dictionaries with 'file_path', 'jq_schema',
                                      'metadata_keys', and 'json_lines' as keys.
        """
        start_time = datetime.now()
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "init",
                    "class": "VectorDB",
                    "description": f"Start vectorDB pipeline at {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                },
                ensure_ascii=False,
            )
        )

        self.data_type = check_index_path_keywords(index_name)
        self.index_name = index_name
        self.weaviate_client.collections.delete(name=index_name)

        documents = self.load_documents(data_paths)
        self.db = self.build_weaviate_index(documents)

        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"index named {self.index_name} has been saved to weaviate server",
                },
                ensure_ascii=False,
            )
        )

        end_time = datetime.now()
        elapsed_time = end_time - start_time

        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"✅ complete vectorDB pipeline at {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                },
                ensure_ascii=False,
            )
        )
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"⏱️ elapsed time: {str(timedelta(seconds=elapsed_time.total_seconds()))}",
                },
                ensure_ascii=False,
            )
        )

    def add(
        self,
        index_name: str,
        new_data_paths: List[Dict[str, Optional[List[str]]]],
    ):
        """
        Function to add new documents to the weaviate database.

        Parameters
        ----------
        index_name (str): Name of the Weaviate collection to store or retrieve documents.
        new_data_paths : List[Dict[str, Optional[List[str]]]]
            A list of dictionaries where each dictionary contains the paths of new data to be added to the weaviate database.
            The keys represent the data types and the values are lists of file paths.
        """
        self.index_name = index_name

        start_time = datetime.now()
        # Load vector database
        self.data_type = check_index_path_keywords(index_name)

        db = CustomWeaviateVectorStore(
            client=self.weaviate_client,
            index_name=self.index_name,
            text_key="text",
            embedding=self.embedding.embedding_model_huggingface,
        )

        # Load additional documents
        documents = self.load_documents(new_data_paths)
        # Check if each document has an index, if not, generate one
        for doc in documents:
            if "index" not in doc.metadata or not doc.metadata["index"]:
                doc.metadata["index"] = generate_uuid5(doc.content)
        ids = [doc.metadata["index"] for doc in documents]

        db.add_documents(documents, ids=ids, client=self.weaviate_client)

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "run",
                    "class": "VectorDB",
                    "description": f"✅ add index to vectorDB {list(set([doc.metadata['index'] for doc in documents]))} at {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                },
                ensure_ascii=False,
            )
        )
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"⏱️ elapsed time: {str(timedelta(seconds=elapsed_time.total_seconds()))}",
                },
                ensure_ascii=False,
            )
        )

    def remove(
        self,
        index_name: str,
        docstore_ids: list,
    ):
        """
        Function to remove documents from the db.

        Parameters
        ----------
        index_name (str): Name of the Weaviate collection to store or retrieve documents.
        docstore_ids : list
            The list of docstore ids to remove. If None, all documents are removed.

        Raises
        ------
        ValueError
            No matching documents found.
            The index values in the response do not match docstore_ids.
        """

        start_time = datetime.now()
        self.index_name = index_name
        db = CustomWeaviateVectorStore(
            client=self.weaviate_client,
            index_name=self.index_name,
            text_key="text",
            embedding=self.embedding,
        )

        set_ids = set(docstore_ids)
        if len(set_ids) != len(docstore_ids):
            raise ValueError("Duplicate ids in list of ids to remove.")
        matching_obj = self.get(self.index_name, docstore_ids)
        if not matching_obj:
            self.logger.debug(
                json.dumps(
                    {
                        "log_type": "run",
                        "class": "VectorDB",
                        "description": f"no matching documents found",
                    },
                    ensure_ascii=False,
                )
            )
            return
        matching_ids = [str(obj.properties["index"]) for obj in matching_obj]

        if sorted(matching_ids) != sorted(docstore_ids):
            raise ValueError(
                f"The index values in the response do not match docstore_ids.\nmatching_ids:{sorted(matching_ids)}, docstore_ids {sorted(docstore_ids)}"
            )

        db.delete(docstore_ids)

        end_time = datetime.now()
        elapsed_time = end_time - start_time
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "run",
                    "class": "VectorDB",
                    "description": f"✅ delete index to vectorDB {docstore_ids} at {end_time.strftime('%Y-%m-%d %H:%M:%S')})",
                },
                ensure_ascii=False,
            )
        )
        self.logger.debug(
            json.dumps(
                {
                    "log_type": "end",
                    "class": "VectorDB",
                    "description": f"⏱️ elapsed time: {str(timedelta(seconds=elapsed_time.total_seconds()))}",
                },
                ensure_ascii=False,
            )
        )

    def embed_query(self, query: str) -> list[float]:
        return self.embedding.embed_query(query)

    def close(self):
        self.weaviate_client.close()
