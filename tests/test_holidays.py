import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the project root to the Python path
# This tells Python where to find the 'src' module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.holidays import _load_config, get_holidays


class TestLoadConfig:
    """Tests for the _load_config helper function"""

    def test_load_config_returns_dict(self):
        """Test that _load_config returns a dictionary"""
        config = _load_config()

        # Assert checks if condition is True, fails test if False
        assert isinstance(config, dict)
        assert "holidays" in config
        assert "api_url" in config["holidays"]


class TestGetHolidays:
    """Tests for the main get_holidays function"""

    def test_get_holidays_success(self):
        """Test that get_holidays returns data when API call succeeds"""

        # Mock response data (what the API would return)
        mock_api_response = {
            "england-and-wales": {
                "division": "england-and-wales",
                "events": [
                    {
                        "title": "New Year's Day",
                        "date": "2024-01-01",
                        "notes": "",
                        "bunting": True,
                    },
                    {
                        "title": "Good Friday",
                        "date": "2024-03-29",
                        "notes": "",
                        "bunting": False,
                    },
                ],
            },
            "scotland": {"division": "scotland", "events": []},
        }

        # @patch replaces the 'get' function with a mock during this test
        with patch("src.holidays.get") as mock_get:
            # Setup: Tell the mock what to return
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response

            # Execute: Call the function we're testing
            result = get_holidays(2024, "GB")

            # Assert: Verify the results
            assert result is not None
            assert "events" in result
            assert len(result["events"]) == 2
            assert result["events"][0]["title"] == "New Year's Day"

            # Verify the API was called with correct URL
            mock_get.assert_called_once()

    def test_get_holidays_api_failure(self):
        """Test that get_holidays handles API errors gracefully"""

        with patch("src.holidays.get") as mock_get:
            # Simulate an API error (404, 500, etc.)
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            # Execute
            result = get_holidays(2024, "GB")

            # Assert: Should return empty list on error
            assert result == []

    def test_get_holidays_uses_config(self):
        """Test that get_holidays uses the URL from config.yaml"""

        mock_api_response = {
            "england-and-wales": {"division": "england-and-wales", "events": []}
        }

        with patch("src.holidays.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response

            get_holidays(2024, "GB")

            # Verify it called the API with the URL from config
            called_url = mock_get.call_args[0][0]
            assert "gov.uk/bank-holidays.json" in called_url


# Fixture example: reusable test data
@pytest.fixture
def sample_holiday_data():
    """
    Fixture provides reusable test data.
    Any test can use this by adding 'sample_holiday_data' as a parameter.
    """
    return {
        "england-and-wales": {
            "division": "england-and-wales",
            "events": [
                {
                    "title": "Christmas Day",
                    "date": "2024-12-25",
                    "notes": "",
                    "bunting": True,
                }
            ],
        }
    }


def test_with_fixture(sample_holiday_data):
    """Example test using the fixture above"""
    assert "england-and-wales" in sample_holiday_data
    assert len(sample_holiday_data["england-and-wales"]["events"]) == 1
