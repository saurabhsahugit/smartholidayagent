from requests import get
from datetime import datetime
from pathlib import Path
import yaml


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)



def get_holidays(year: int, country_code: str) -> list:
    """
    Fetches public holidays for a given year and country code using the Nager.Date API.

    Args:
        year (int): The year for which to fetch holidays.
        country_code (str): The ISO 3166-1 alpha-2 country code (e.g., 'GB' for the UK).

    Returns:
        list: A list of dictionaries containing holiday information.
    """

    def get_current_year():
        return datetime.now().year
    
    url = f"https://www.gov.uk/bank-holidays.json"
    config=_load_config()
    response = get(config["holidays"]["api_url"])

    if response.status_code == 200:
        holidays = response.json()
        england_and_wales_holidays = holidays["england-and-wales"]
        print(f"Holidays for {get_current_year()} in england-and-wales: {england_and_wales_holidays}" )
        return england_and_wales_holidays
    else:
        print(f"Error fetching holidays: {response.status_code}")
        return []