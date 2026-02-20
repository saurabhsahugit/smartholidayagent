from __future__ import annotations

from datetime import date

import pytest

from smartholidayagent.services.govuk_holidays import GovUkHolidayClient


@pytest.mark.asyncio
async def test_parse_england_and_wales_from_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    client = GovUkHolidayClient()

    async def fake_get_raw():
        return {
            "england-and-wales": {
                "division": "england-and-wales",
                "events": [
                    {"title": "New Year’s Day", "date": "2026-01-01", "notes": "", "bunting": True},
                    {"title": "Christmas Day", "date": "2026-12-25", "notes": "", "bunting": True},
                ],
            }
        }

    monkeypatch.setattr(client, "get_raw", fake_get_raw)

    holidays = await client.get_england_and_wales_holidays()
    assert [h.date for h in holidays] == [date(2026, 1, 1), date(2026, 12, 25)]
    assert holidays[0].title == "New Year’s Day"