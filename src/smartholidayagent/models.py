from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start: date
    end: date

    @property
    def is_valid(self) -> bool:
        return self.start <= self.end


class TripLengthRange(BaseModel):
    min_days: Annotated[int, Field(ge=1, le=365)]
    max_days: Annotated[int, Field(ge=1, le=365)]

    @property
    def is_valid(self) -> bool:
        return self.min_days <= self.max_days


class Preferences(BaseModel):
    total_annual_leave: Annotated[int, Field(ge=0, le=366)]
    max_days_per_trip: Annotated[int, Field(ge=1, le=366)]

    # Users can provide multiple ranges; for the form we'll accept a comma-separated input.
    preferred_trip_length_ranges: list[TripLengthRange] = Field(default_factory=list)

    # Blocked periods user cannot travel; for the form we'll accept one range per line.
    blocked_periods: list[DateRange] = Field(default_factory=list)