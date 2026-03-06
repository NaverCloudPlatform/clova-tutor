# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from fastapi import Depends

from users.database.repository.unknown_concept_repo import UserUnknownConceptRepository
from users.database.repository.user_repo import UserRepository
from users.service.user_service import UserService
from users.service.user_unknown_concept_service import UserUnknownConceptService
from users.usecase.user_unknown_concept_usecase import UserUnknownConceptUseCase
from users.usecase.user_usecase import UserUseCase

# 레포 의존성

async def get_user_repo(
) -> UserRepository:
    return UserRepository()


async def get_user_unknown_concept_repo(
) -> UserUnknownConceptRepository:
    return UserUnknownConceptRepository()

# 서비스 의존성

async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserService:
    return UserService(
        user_repo=user_repo
    )


async def get_user_unknown_concept_service(
    unknown_concept_repo: UserUnknownConceptRepository = Depends(get_user_unknown_concept_repo)
) -> UserUnknownConceptService:
    return UserUnknownConceptService(
        unknown_concept_repo=unknown_concept_repo
    )

# 유즈케이스 의존성

async def get_user_usecase(
    user_service: UserService = Depends(get_user_service)
) -> UserUseCase:
    return UserUseCase(
        user_service=user_service
    )


async def get_user_unknown_concept_usecase(
    user_service: UserService = Depends(get_user_service),
    user_unknown_concept_service: UserUnknownConceptService = Depends(get_user_unknown_concept_service)
) -> UserUnknownConceptUseCase:
    return UserUnknownConceptUseCase(
        user_service=user_service,
        unknown_concept_service=user_unknown_concept_service
    )
