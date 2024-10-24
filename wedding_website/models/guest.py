import dataclasses
from functools import cached_property
from typing import Optional

from wedding_website.db import get_db_cursor
from wedding_website.exceptions import GuestNotFoundError


@dataclasses.dataclass
class Guest:
    id: int
    household_id: int
    name: str
    is_plus_one: bool
    wedding_response: bool
    dinner_response: bool
    brunch_response: bool
    updated: str  # Assuming 'updated' is stored as a TEXT timestamp in SQLite

    @classmethod
    def from_alias(cls, alias: str) -> "Guest":
        with get_db_cursor() as cursor:
            query = """
            SELECT g.id, g.household_id, g.name, g.is_plus_one, g.wedding_response,
                   g.dinner_response, g.brunch_response, g.updated
            FROM guest g
            JOIN guest_to_alias gta ON g.id = gta.guest_id
            WHERE gta.alias = ?
            """
            cursor.execute(query, (alias,))
            row = cursor.fetchone()
        if row is None:
            raise GuestNotFoundError(f"Guest with alias {alias} not found")
        guest = cls(*row)
        return guest

    @property
    def plus_one_owner(self) -> Optional["Guest"]:
        if self.is_plus_one:
            with get_db_cursor() as cursor:
                query = "SELECT * FROM GUEST WHERE household_id = ? AND is_plus_one = 0;"
                cursor.execute(query, (self.household_id,))
                row = cursor.fetchone()
            return Guest(*row)
        return None

    @property
    def pretty_name(self) -> str:
        if self.is_plus_one:
            assert self.plus_one_owner is not None
            if self.name:
                return f"{self.name}"
            else:
                return f"{self.plus_one_owner.name}'s +1"
        return self.name

    @cached_property
    def household(self) -> "Household":  # type: ignore  # noqa: F821
        from wedding_website.models.household import Household

        return Household.from_id(self.household_id)

    def save(self) -> None:
        with get_db_cursor() as cursor:
            query = """
            UPDATE guest
            SET name = ?, wedding_response = ?, dinner_response = ?, brunch_response = ?
            WHERE id = ?
            """
            cursor.execute(
                query, (self.name, self.wedding_response, self.dinner_response, self.brunch_response, self.id)
            )
            cursor.connection.commit()
