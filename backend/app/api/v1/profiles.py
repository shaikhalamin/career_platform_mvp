"""User profile endpoints: `/profiles` CRUD.

Routes are thin by design: validate with the request schemas, delegate to
`profile_service`, and wrap the result in the standard envelope. Error
responses (404, 409, 422, …) come from the service-raised `AppError`s and
the global exception handlers — never from try/except blocks here.
"""

from fastapi import APIRouter, status

from app.core.dependencies import PaginationDep, SessionDep
from app.core.responses import ApiResponse, build_pagination_meta
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post(
    "",
    response_model=ApiResponse[ProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a profile",
    description="Creates a user profile with a display name and a unique email address.",
)
async def create_profile(payload: ProfileCreate, session: SessionDep) -> ApiResponse[ProfileRead]:
    profile = await profile_service.create_profile(session, payload)
    return ApiResponse[ProfileRead](
        data=ProfileRead.model_validate(profile), message="Profile created."
    )


@router.get(
    "",
    response_model=ApiResponse[list[ProfileRead]],
    summary="List profiles (paginated)",
)
async def list_profiles(
    session: SessionDep, pagination: PaginationDep
) -> ApiResponse[list[ProfileRead]]:
    items, total = await profile_service.list_profiles(
        session, page=pagination.page, page_size=pagination.page_size
    )
    return ApiResponse[list[ProfileRead]](
        data=[ProfileRead.model_validate(item) for item in items],
        meta=build_pagination_meta(pagination.page, pagination.page_size, total),
    )


@router.get(
    "/{profile_id}",
    response_model=ApiResponse[ProfileRead],
    summary="Get a profile by id",
)
async def get_profile(profile_id: int, session: SessionDep) -> ApiResponse[ProfileRead]:
    profile = await profile_service.get_profile(session, profile_id)
    return ApiResponse[ProfileRead](data=ProfileRead.model_validate(profile))


@router.patch(
    "/{profile_id}",
    response_model=ApiResponse[ProfileRead],
    summary="Update a profile (partial)",
    description="Send only changed fields; an explicit `null` is treated as no change.",
)
async def update_profile(
    profile_id: int, payload: ProfileUpdate, session: SessionDep
) -> ApiResponse[ProfileRead]:
    profile = await profile_service.update_profile(session, profile_id, payload)
    return ApiResponse[ProfileRead](
        data=ProfileRead.model_validate(profile), message="Profile updated."
    )


@router.delete(
    "/{profile_id}",
    response_model=ApiResponse[None],
    summary="Delete a profile",
)
async def delete_profile(profile_id: int, session: SessionDep) -> ApiResponse[None]:
    await profile_service.delete_profile(session, profile_id)
    return ApiResponse[None](data=None, message="Profile deleted.")
