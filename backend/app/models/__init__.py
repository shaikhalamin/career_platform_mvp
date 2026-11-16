"""Aggregate model imports.

Alembic autogenerate (and anything else traversing `Base.metadata`) sees the
tables only through this package — every new model module must be imported
here.
"""

from app.models.opportunity import Opportunity
from app.models.shortlist_item import ShortlistItem
from app.models.user_profile import UserProfile

__all__ = ["Opportunity", "ShortlistItem", "UserProfile"]
