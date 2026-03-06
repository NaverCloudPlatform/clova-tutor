# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import base64
from enum import StrEnum
import json
import http.client
from http import HTTPStatus
import time
from typing import Optional, List

import numpy as np
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from requests.exceptions import RequestException
from huggingface_hub.errors import HfHubHTTPError
from langchain_core.embeddings import Embeddings
from langchain_huggingface.embeddings import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpointEmbeddings,
)

from config.config import huggingface_config,  clovastudio_config, fireworks_config

class EmbeddingType(StrEnum):
    CLOVA_STUDIO = "clovastudio"
    FIREWORKS = "fireworks"
    HUGGINGFACE = "huggingface"

class CustomEmbedding(Embeddings):
    def __init__(
        self,
        wait_mode: bool =False, 
        embedding_type: EmbeddingType = EmbeddingType.CLOVA_STUDIO,
    ) -> None:
        super().__init__()
        self.wait_mode = wait_mode
        self.count = 0
        # HCX id, secret get
        self.embed_dimension = 1024
        self.embedding_type = embedding_type

        huggingfacehub_api_token = huggingface_config.HUGGINGFACE_EMBEDDING_KEY
        # default: local load
        self.embedding_model_huggingface = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
        )

        if self.embedding_type == EmbeddingType.CLOVA_STUDIO:  # default = hcx, ncp1
            self.embedding_model_API = ApiToolExecutor(
                host=clovastudio_config.CLOVA_STUDIO_HOST,
                url=clovastudio_config.CLOVA_STUDIO_URL,
                client_id=clovastudio_config.CLOVA_STUDIO_REQUEST_ID,
                client_secret=clovastudio_config.CLOVA_STUDIO_GW_API_KEY,
                app_id=clovastudio_config.CLOVA_STUDIO_APP_ID,
                access_token=clovastudio_config.CLOVA_STUDIO_API_KEY,
                wait_mode=self.wait_mode,
            )
        elif self.embedding_type == EmbeddingType.FIREWORKS:
            self.embedding_model_API = ApiToolExecutor(
                host=fireworks_config.FIREWORKS_HOST,
                url=fireworks_config.FIREWORKS_URL,
                client_id=fireworks_config.FIREWORKS_CLIENT_ID,
                client_secret=fireworks_config.FIREWORKS_CLIENT_SECRET,
                app_id=fireworks_config.FIREWORKS_APP_ID,
                access_token=fireworks_config.FIREWORKS_ACCESS_TOKEN,
                wait_mode=self.wait_mode,
                fireworks_embedding=True,
            )
        elif self.embedding_type == EmbeddingType.HUGGINGFACE:
            if wait_mode:
                self.embedding_model = self.embedding_model_huggingface
            else:
                self.embedding_model = RetryHuggingFaceEndpointEmbeddings(
                    model="BAAI/bge-m3",
                    task="feature-extraction",
                    huggingfacehub_api_token=huggingfacehub_api_token,
                )

    def embed_documents(
        self,
        texts: List[str],
        chunk_size: Optional[int] = 0,
        embedding_type: Optional[str] = None,
    ) -> List[List[float]]:
        """Call out to HCX's embedding endpoint for embedding search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings. If None, will use the chunk size
                specified by the class.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings: List[List[float]] = []
        for text in texts:
            request_data = (
                {"input": text, "model": self.embedding_model, "dimensions": 768}
                if embedding_type == "fireworks"
                else {"text": text}
            )

            response = self.embedding_model_API.execute(request_data)
            if isinstance(response, str) and response == "Error":
                if self.wait_mode:
                    print("HCX server error: Please try again after a wait.")
                    break
                else:
                    return None

            embedding = np.array([response], dtype=np.float32)
            if embedding_type == "clovastudio":
                norm = np.linalg.norm(embedding, axis=1, keepdims=True)
                embedding = embedding / norm
            embeddings.append(embedding[0])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Call out to HCX's embedding endpoint for embedding query text.
        If a rate-limit error occurs in the user query, Hugging Face BGE embedding will be used.

        Args:
            text: The text to embed.

        Returns:
            Embedding for the text.
        """
        embeddings = self.embed_documents([text], embedding_type=self.embedding_type)
        if not embeddings and self.embedding_type == "clovastudio":
            print(
                "Using huggingface inference Embedding - clovastudio embedding hit rate limit"
            )
            hgb = self.embedding_model_huggingface.embed_query(text)
            formatted_hgb = [round(x, 8) for x in hgb]
            return formatted_hgb
        else:
            return embeddings[0]


class ApiToolExecutor:
    def __init__(
        self,
        host,
        url=None,
        client_id=None,
        client_secret=None,
        access_token=None,
        app_id=None,
        wait_mode=False,
        fireworks_embedding=False,
    ):
        self._host = host
        self._fireworks_embedding = fireworks_embedding
        # client_id and client_secret are used to issue access_token.
        # You should not share this with others.
        self._client_id = client_id
        self._client_secret = client_secret
        self._app_id = app_id
        # Base64Encode(client_id:client_secret)
        self._encoded_secret = base64.b64encode(
            "{}:{}".format(self._client_id, self._client_secret).encode("utf-8")
        ).decode("utf-8")
        self._access_token = access_token
        if self._fireworks_embedding:
            # if fireworks embedding
            self._url = url
            self._content_type = "application/json"
        else:
            # if hcx embedding
            self._url = f"/{url}/{self._app_id}"
            self._content_type = "application/json; charset=utf-8"
        self.wait_mode = wait_mode

    def _refresh_access_token(self):
        headers = {"Authorization": "Basic {}".format(self._encoded_secret)}
        conn = http.client.HTTPSConnection(self._host)
        # If existingToken is true, it returns a token that has the longest expiry time among existing tokens.
        conn.request("GET", "/v1/auth/token?existingToken=true", headers=headers)
        response = conn.getresponse()
        body = response.read().decode()
        conn.close()

        token_info = json.loads(body)
        self._access_token = token_info["result"]["accessToken"]

    def _send_request(self, completion_request):
        if self._fireworks_embedding:
            headers = {
                "Authorization": "Bearer {}".format(self._access_token),
                "Content-Type": self._content_type,
            }
        else:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "X-NCP-CLOVASTUDIO-API-KEY": self._access_token,
                "X-NCP-APIGW-API-KEY": self._client_secret,
                "X-NCP-CLOVASTUDIO-REQUEST-ID": self._client_id,
            }
        try:
            conn = http.client.HTTPSConnection(self._host)
            conn.request(
                "POST",
                self._url,
                body=json.dumps(completion_request),
                headers=headers,
            )
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding="utf-8"))
        status = response.status
        conn.close()
        return result, status

    def execute(self, completion_request):
        if self._access_token is None:
            self._refresh_access_token()
        res, status = self._send_request(completion_request)
        if status == HTTPStatus.UNAUTHORIZED:
            # Check whether the token has expired and reissue the token.
            self._access_token = None
            return self.execute(completion_request)
        elif status == HTTPStatus.OK:
            if self._fireworks_embedding:
                return res["data"][0]["embedding"]
            else:
                return res["result"]["embedding"]
        else:
            if self.wait_mode:
                # DOCS 저장시 wait_mode = True
                message = res["status"]["message"]
                print(
                    f"{message}- The process will resume from the embedding after 65 seconds ..."
                )

                time.sleep(65)
                res, status = self._send_request(completion_request)
                if status == HTTPStatus.OK:
                    return res["result"]["embedding"]
                else:
                    return "Error"
            else:
                return "Error"


class RetryHuggingFaceEndpointEmbeddings(HuggingFaceEndpointEmbeddings):
    """HuggingFaceHub embedding with retry logic."""

    max_batch_size: int = 50

    def _chunked(self, texts: List[str], size: int) -> List[List[str]]:
        return [texts[i : i + size] for i in range(0, len(texts), size)]

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type(
            (RequestException, TimeoutError, ConnectionError, HfHubHTTPError)
        ),
    )
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        _model_kwargs = self.model_kwargs or {}
        all_embeddings = []
        for chunk in self._chunked(texts, self.max_batch_size):
            responses = self.client.post(
                json={"inputs": chunk, **_model_kwargs}, task=self.task
            )
            all_embeddings.extend(json.loads(responses.decode()))

        return all_embeddings

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type(
            (RequestException, TimeoutError, ConnectionError, HfHubHTTPError)
        ),
    )
    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type(
            (RequestException, TimeoutError, ConnectionError, HfHubHTTPError)
        ),
    )
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        _model_kwargs = self.model_kwargs or {}
        responses = await self.async_client.post(
            json={"inputs": texts, "parameters": _model_kwargs}, task=self.task
        )
        return json.loads(responses.decode())

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        retry=retry_if_exception_type(
            (RequestException, TimeoutError, ConnectionError, HfHubHTTPError)
        ),
    )
    async def aembed_query(self, text: str) -> List[float]:
        return (await self.aembed_documents([text]))[0]
