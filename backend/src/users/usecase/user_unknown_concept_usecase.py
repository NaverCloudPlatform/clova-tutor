# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from uuid import UUID

from users.domain.user import User
from users.presentation.schemas.request_dto import UnknownConceptCreateRequestBody
from users.presentation.schemas.response_dto import UnknownConceptResponse
from users.service.exceptions import UserNotFoundException, UserUnknownConceptNotFoundException
from users.service.user_service import UserService
from users.service.user_unknown_concept_service import UserUnknownConceptService


class UserUnknownConceptUseCase:
    def __init__(
        self,
        user_service: UserService,
        unknown_concept_service: UserUnknownConceptService
    ):
        self.user_service = user_service
        self.unknown_concept_service = unknown_concept_service

    async def _validate_user(self, user_id: UUID) -> User:
        user = await self.user_service.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user


    async def list_unknown_concepts(
        self,
        user_id: UUID,
        subject: str | None
    ) -> list[UnknownConceptResponse]:
        await self._validate_user(user_id)

        concepts = await self.unknown_concept_service.list_concepts_by_user_id(
            user_id=user_id,
            subject=subject
        )

        return [UnknownConceptResponse.model_validate(c) for c in concepts]


    async def upsert_concept(
        self,
        user_id: UUID,
        body: UnknownConceptCreateRequestBody
    ) -> UnknownConceptResponse:
        await self._validate_user(user_id)

        need_to_create = False
        try:
            concept = await self.unknown_concept_service.get_concepts_by_user_id_and_subject_and_key_concept(
                user_id=user_id,
                subject=body.subject,
                key_concept=body.key_concept
            )
        except UserUnknownConceptNotFoundException:
            need_to_create = True

        if need_to_create:
            new_concept = await self.unknown_concept_service.create_user_unknown_concept(
                user_id=user_id,
                subject=body.subject,
                key_concept=body.key_concept,
                unknown_concept=body.unknown_concept,
                unknown_concept_reason=body.unknown_concept_reason
            )
            return UnknownConceptResponse.model_validate(new_concept)

        updated_concept = await self.unknown_concept_service.update_user_unknown_concept_and_reason_by_id(
            id = concept.id,
            unknown_concept=body.unknown_concept,
            unknown_concept_reason=body.unknown_concept_reason
        )
        return UnknownConceptResponse.model_validate(updated_concept)


    async def delete_concept(
        self,
        user_id: UUID,
        subject: str | None,
        key_concept: str | None
    ) -> None:
        await self.unknown_concept_service.delete_by_user_id(
            user_id,
            subject=subject,
            key_concept=key_concept
        )

