# Create a quick test file in your project root

from src.holidays import get_holidays

if __name__ == "__main__":
    holidays = get_holidays(2024, "england-and-wales")
    print(f"Found {len(holidays)} holidays")
    print(holidays)
