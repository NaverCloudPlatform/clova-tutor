from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelRequest(_message.Message):
    __slots__ = ("chat_id", "subject", "grade", "user_id", "user_name", "user_query", "image_url", "vector_problem_id", "translation_button", "request_id")
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    GRADE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_QUERY_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    VECTOR_PROBLEM_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSLATION_BUTTON_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: int
    subject: str
    grade: int
    user_id: str
    user_name: str
    user_query: str
    image_url: _containers.RepeatedScalarFieldContainer[str]
    vector_problem_id: str
    translation_button: bool
    request_id: str
    def __init__(self, chat_id: _Optional[int] = ..., subject: _Optional[str] = ..., grade: _Optional[int] = ..., user_id: _Optional[str] = ..., user_name: _Optional[str] = ..., user_query: _Optional[str] = ..., image_url: _Optional[_Iterable[str]] = ..., vector_problem_id: _Optional[str] = ..., translation_button: bool = ..., request_id: _Optional[str] = ...) -> None: ...

class CreateChatTitleRequest(_message.Message):
    __slots__ = ("user_input",)
    USER_INPUT_FIELD_NUMBER: _ClassVar[int]
    user_input: str
    def __init__(self, user_input: _Optional[str] = ...) -> None: ...

class RecommendationInfo(_message.Message):
    __slots__ = ("recommend_tool", "recommended_problem_id")
    RECOMMEND_TOOL_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_PROBLEM_ID_FIELD_NUMBER: _ClassVar[int]
    recommend_tool: bool
    recommended_problem_id: str
    def __init__(self, recommend_tool: bool = ..., recommended_problem_id: _Optional[str] = ...) -> None: ...

class PresentationOption(_message.Message):
    __slots__ = ("response_style", "has_translation_response")
    RESPONSE_STYLE_FIELD_NUMBER: _ClassVar[int]
    HAS_TRANSLATION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response_style: str
    has_translation_response: bool
    def __init__(self, response_style: _Optional[str] = ..., has_translation_response: bool = ...) -> None: ...

class ModelResponse(_message.Message):
    __slots__ = ("id", "created", "finish", "model_response", "subject", "reference_image_document", "recommendation", "presentation")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    FINISH_FIELD_NUMBER: _ClassVar[int]
    MODEL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_IMAGE_DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    PRESENTATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: int
    finish: bool
    model_response: str
    subject: str
    reference_image_document: _containers.RepeatedScalarFieldContainer[str]
    recommendation: RecommendationInfo
    presentation: _containers.RepeatedCompositeFieldContainer[PresentationOption]
    def __init__(self, id: _Optional[str] = ..., created: _Optional[int] = ..., finish: bool = ..., model_response: _Optional[str] = ..., subject: _Optional[str] = ..., reference_image_document: _Optional[_Iterable[str]] = ..., recommendation: _Optional[_Union[RecommendationInfo, _Mapping]] = ..., presentation: _Optional[_Iterable[_Union[PresentationOption, _Mapping]]] = ...) -> None: ...

class CreateChatTitleResponse(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...
