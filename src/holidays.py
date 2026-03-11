from requests import get
from requests.exceptions import RequestException
from datetime import datetime
from pathlib import Path
import yaml


VALID_REGIONS = {"england-and-wales", "scotland", "northern-ireland"}


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_holidays(year: int, region: str) -> list[dict]:
    """
    Fetches UK public holidays for a given year and region from GOV.UK.

    Args:
        year (int): Year to filter holidays by (e.g. 2026).
        region (str): One of england-and-wales, scotland, northern-ireland.

    Returns:
        list[dict]: Holiday events for the given year/region.
    """
    if year < 1900 or year > 2100:
        raise ValueError("year must be between 1900 and 2100")
    if region not in VALID_REGIONS:
        raise ValueError(f"invalid region: {region}")

    config = _load_config()
    api_url = config["holidays"]["api_url"]

    try:
        response = get(api_url, timeout=10)
    except RequestException:
        return []

    if response.status_code != 200:
        return []

    payload = response.json()
    region_data = payload.get(region)
    if not isinstance(region_data, dict):
        raise HolidayFetchError(f"Missing/invalid region data: {region}")

    events = region_data.get("events")
    if not isinstance(events, list):
        raise HolidayFetchError(f"Missing/invalid events list for region: {region}")

    filtered = [e for e in events if e["date"].startswith(str(year))]
    return [
        {"title": e["title"], "date": e["date"], "notes": e.get("notes", "")}
        for e in filtered
    ]