from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

GOVUK_BANK_HOLIDAYS_JSON = "https://www.gov.uk/bank-holidays.json"


@dataclass(frozen=True)
class BankHoliday:
    title: str
    date: date
    notes: str | None = None
    bunting: bool | None = None


class GovUkHolidayClient:
    """
    Fetches GOV.UK bank holidays and caches them in-memory for a TTL.
    """

    def __init__(self, *, timeout_s: float = 10.0, cache_ttl: timedelta = timedelta(hours=6)) -> None:
        self._timeout_s = timeout_s
        self._cache_ttl = cache_ttl
        self._cache_expires_at: datetime | None = None
        self._cache_data: dict[str, Any] | None = None

    async def _fetch_json(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout_s) as client:
            resp = await client.get(GOVUK_BANK_HOLIDAYS_JSON, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()

    async def get_raw(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        if self._cache_data is not None and self._cache_expires_at is not None:
            if now < self._cache_expires_at:
                return self._cache_data

        data = await self._fetch_json()
        self._cache_data = data
        self._cache_expires_at = now + self._cache_ttl
        return data

    async def get_england_and_wales_holidays(self) -> list[BankHoliday]:
        data = await self.get_raw()
        division = data.get("england-and-wales", {})
        events = division.get("events", [])

        holidays: list[BankHoliday] = []
        for ev in events:
            # Example: {"title": "...", "date": "2026-12-25", "notes": "", "bunting": true}
            d = date.fromisoformat(ev["date"])
            holidays.append(
                BankHoliday(
                    title=str(ev.get("title", "")),
                    date=d,
                    notes=(ev.get("notes") if ev.get("notes") not in ("", None) else None),
                    bunting=ev.get("bunting"),
                )
            )

        holidays.sort(key=lambda h: h.date)
        return holidays

    async def get_upcoming_england_and_wales(self, *, from_date: date | None = None) -> list[BankHoliday]:
        if from_date is None:
            from_date = date.today()
        all_holidays = await self.get_england_and_wales_holidays()
        return [h for h in all_holidays if h.date >= from_date]