# Create a quick test file in your project root

from src.holidays import get_holidays
holidays = get_holidays(2024, 'GB')
print(f'Found {len(holidays)} holidays')
print(holidays)
