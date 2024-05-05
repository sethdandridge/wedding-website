import dataclasses

from flask import current_app

from wedding_website.db import get_db_cursor
from wedding_website.exceptions import HouseholdNotFoundError
from wedding_website.models.guest import Guest


@dataclasses.dataclass
class Household:
    id: int
    cute_name: str
    is_invited_dinner: bool
    is_invited_brunch: bool

    @classmethod
    def from_id(cls, household_id: int) -> "Household":
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM household WHERE guest_id = ?", (household_id,))
            row = cursor.fetchone()
        if row is None:
            raise HouseholdNotFoundError(f"Household with guest_id {household_id} not found")
        return cls(*row)

    @classmethod
    def from_cute_name(cls, cute_name: str) -> "Household":
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM household WHERE cute_name = ?", (cute_name,))
            row = cursor.fetchone()
        if row is None:
            raise HouseholdNotFoundError(f"Household with cute name {cute_name} not found")
        return cls(*row)

    @property
    def guests(self) -> list[Guest]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM guest WHERE household_id = ? ORDER BY guest_id;", (self.id,))
            rows = cursor.fetchall()
        guests = [Guest(*row) for row in rows]
        current_app.logger.info(f"Found {guests} guests for household {self.id}")
        return guests

    @property
    def cute_subdomain(self) -> str:
        return self.cute_name.replace("-", ".")
