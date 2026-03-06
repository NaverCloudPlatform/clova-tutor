# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import re
from typing import Any, List, Optional, Tuple, Union

import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_core.documents import Document


def parse_and_normalize_scores(
    explain_score: str, bm25_max=7.5, vector_max=1.0
) -> dict:
    scores = {}
    bm25_match = re.search(r"keyword,bm25\).*?original score ([\d\.]+)", explain_score)
    vec_match = re.search(
        r"vector,hybridVector\).*?original score ([\d\.]+)", explain_score
    )

    if bm25_match:
        raw = float(bm25_match.group(1))
        scores["bm25"] = raw
        scores["bm25_normalized"] = min(raw / bm25_max, 1.0)
    if vec_match:
        raw = float(vec_match.group(1))
        scores["vector"] = raw
        scores["vector_normalized"] = min(raw / vector_max, 1.0)

    return scores


def compute_manual_hybrid_score(scores: dict, alpha=0.7):
    b = scores.get("bm25_normalized", 0)
    v = scores.get("vector_normalized", 0)
    return alpha * v + (1 - alpha) * b


class CustomWeaviateVectorStore(WeaviateVectorStore):
    """Custom vector store with overridden search logic."""

    def _perform_search(
        self,
        query: Optional[str],
        k: int,
        return_score: bool = False,
        alpha: float = 0.7,
        tenant: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[List[Document], List[Tuple[Document, float]]]:
        """
        Perform a similarity search.

        Parameters:
        query (str): The query string to search for.
        k (int): The number of results to return.
        return_score (bool, optional): Whether to return the score along with the
          document. Defaults to False.
        tenant (Optional[str], optional): The tenant name. Defaults to None.
        **kwargs: Additional parameters to pass to the search method. These parameters
          will be directly passed to the underlying Weaviate client's search method.

        Returns:
        List[Union[Document, Tuple[Document, float]]]: A list of documents that match
          the query. If return_score is True, each document is returned as a tuple
          with the document and its score.

        Raises:
        ValueError: If _embedding is None or an invalid search method is provided.
        """
        if self._embedding is None:
            raise ValueError("_embedding cannot be None for similarity_search")

        if "return_metadata" not in kwargs:
            kwargs["return_metadata"] = ["score", "explain_score"]
        elif "score" not in kwargs["return_metadata"]:
            kwargs["return_metadata"].append("score")
        elif "explain_score" not in kwargs["return_metadata"]:
            kwargs["return_metadata"].append("explain_score")

        if (
            "return_properties" in kwargs
            and self._text_key not in kwargs["return_properties"]
        ):
            kwargs["return_properties"].append(self._text_key)

        vector = kwargs.pop("vector", None)

        # workaround to handle test_max_marginal_relevance_search
        if vector is None:
            if query is None:
                # raise an error because weaviate will do a fetch object query
                # if both query and vector are None
                raise ValueError("Either query or vector must be provided.")
            else:
                vector = self._embedding.embed_query(query)

        return_uuids = kwargs.pop("return_uuids", False)

        with self._tenant_context(tenant) as collection:
            try:
                result = collection.query.hybrid(
                    query=query, vector=vector, limit=k, **kwargs
                )
            except weaviate.exceptions.WeaviateQueryException as e:
                raise ValueError(f"Error during query: {e}")

        docs_and_scores: List[Tuple[Document, float]] = []
        for obj in result.objects:
            text = obj.properties.pop(self._text_key)
            filtered_metadata = {
                k: v
                for k, v in obj.metadata.__dict__.items()
                if v is not None and k != "score"
            }
            merged_props = {
                **obj.properties,
                **filtered_metadata,
                **({"vector": obj.vector["default"]} if obj.vector else {}),
                **({"uuid": str(obj.uuid)} if return_uuids else {}),
            }
            doc = Document(page_content=text, metadata=merged_props)
            # score = obj.metadata.score -> custom_score
            scores = parse_and_normalize_scores(obj.metadata.explain_score)
            custom_score = compute_manual_hybrid_score(scores, alpha=alpha)
            docs_and_scores.append((doc, custom_score))

        if return_score:
            return docs_and_scores
        else:
            return [doc for doc, _ in docs_and_scores]

    def similarity_search_with_score(
        self, query: str, k: int = 4, alpha=0.7, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """
        Return list of documents most similar to the query
        text and cosine distance in float for each.
        Lower score represents more similarity.
        """

        results = self._perform_search(
            query, k, return_score=True, alpha=alpha, **kwargs
        )

        return results
