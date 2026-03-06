# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from users.database.repository.unknown_concept_repo import (
    UserUnknownConceptFilter,
    UserUnknownConceptRepository,
)
from users.domain.user_unknown_concept import UserUnknownConcept, UserUnknownConceptWithDate
from users.service.exceptions import UserUnknownConceptNotFoundException


class UserUnknownConceptService:
    def __init__(
        self,
        unknown_concept_repo: UserUnknownConceptRepository
    ):
        self.unknown_concept_repo = unknown_concept_repo


    async def get_concepts_by_user_id_and_subject_and_key_concept(
        self,
        user_id: UUID,
        subject: str,
        key_concept: str
    ) -> UserUnknownConcept:
        concept: UserUnknownConcept | None = await self.unknown_concept_repo.get(
            flt=UserUnknownConceptFilter(
                user_id=user_id,
                subject=subject,
                key_concept=key_concept
            )
        )
        if concept is None:
            raise UserUnknownConceptNotFoundException(user_id=user_id, subject=subject, key_concept=key_concept)
        return concept

    async def list_concepts_by_user_id(
        self,
        user_id: UUID,
        *,
        subject: str | None = None,
    ) -> list[UserUnknownConceptWithDate]:
        """사용자의 이해하지 못한 개념 목록을 조회합니다.

        Args:
            user_id (str | UUID): 사용자 ID
            subject (Optional[str]): 과목명으로 필터링. Defaults to None

        Returns:
            List[UserUnknownConcept]: 이해하지 못한 개념 목록 DTO
        """

        concepts = await self.unknown_concept_repo.get_list(
            flt=UserUnknownConceptFilter(user_id=user_id, subject=subject),
            convert_schema=False
        )
        return [UserUnknownConceptWithDate.model_validate(concept) for concept in concepts]

    async def create_user_unknown_concept(
        self,
        user_id: UUID,
        subject: str,
        key_concept: str,
        unknown_concept: str,
        unknown_concept_reason: str | None
    ) -> UserUnknownConceptWithDate:
        new_concept = UserUnknownConcept(
            user_id=user_id,
            subject=subject,
            key_concept=key_concept,
            unknown_concept=unknown_concept,
            unknown_concept_reason=unknown_concept_reason
        )
        cc = await self.unknown_concept_repo.create(new_concept, convert_schema=False)
        return UserUnknownConceptWithDate.model_validate(cc)

    async def update_user_unknown_concept_and_reason_by_id(
        self,
        id: int,
        *,
        unknown_concept: str,
        unknown_concept_reason: str | None
    ) -> UserUnknownConceptWithDate:
        # user_id, subject, key_concept 을 통해 row를 특정합니다. (idx 기반)
        # 이후, 해당 unknown_concept 과 unkown_concept_reason 을 업데이트 합니다.
        cc_model = await self.unknown_concept_repo.get(
            flt=UserUnknownConceptFilter(id=id),
            convert_schema=False
        )
        if cc_model is None:
            raise UserUnknownConceptNotFoundException()

        updated = await self.unknown_concept_repo.update_from_model(
            cc_model,
            update={
                UserUnknownConcept.FIELD_UNKNOWN_CONCEPT: unknown_concept,
                UserUnknownConcept.FIELD_UNKNOWN_CONCEPT_REASON: unknown_concept_reason
            },
            convert_schema=False
        )
        return UserUnknownConceptWithDate.model_validate(updated)

    async def delete_by_user_id(
        self,
        user_id: UUID,
        *,
        subject: str | None = None,
        key_concept: str | None = None
    ) -> None:
        """사용자의 이해하지 못한 개념을 삭제합니다.
        Args:
            user_id (str | UUID) : 유저 Id
            subject (Optional[str], optional): 과목명으로 필터링. Defaults to None
            key_concept (Optional[str], optional): 주요 개념으로 필터링. Defaults to None
        """

        await self.unknown_concept_repo.delete(
            UserUnknownConceptFilter(
                user_id=user_id,
                subject=subject,
                key_concept=key_concept
            )
        )
