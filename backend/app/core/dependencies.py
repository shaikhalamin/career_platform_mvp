"""Shared FastAPI dependencies: DB session injection + list pagination."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

#: Router parameter annotation: `session: SessionDep` injects the request
#: session (committed by `get_db` on success).
SessionDep = Annotated[AsyncSession, Depends(get_db)]

MAX_PAGE_SIZE = 100


@dataclass(slots=True)
class PaginationParams:
    """Common list-endpoint query parameters (1-based pages, bounded size).

    Annotation: `pagination: PaginationDep` — FastAPI reads the Query
    defaults from the dataclass fields.
    """

    page: int = Query(1, ge=1, description="Page number (1-based).")
    page_size: int = Query(
        20, ge=1, le=MAX_PAGE_SIZE, description=f"Items per page (1-{MAX_PAGE_SIZE})."
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


PaginationDep = Annotated[PaginationParams, Depends()]
