from unittest.mock import patch, Mock

import pytest

from weather import get_weather

_MOCK_DATA = {
    "current_condition": [{"temp_C": "22", "weatherDesc": [{"value": "晴れ"}]}],
    "weather": [{
        "maxtempC": "28",
        "mintempC": "18",
        "hourly": [
            {"time": "600",  "tempC": "22", "chanceofrain": "10", "weatherDesc": [{"value": "晴れ"}]},
            {"time": "1200", "tempC": "26", "chanceofrain": "30", "weatherDesc": [{"value": "曇り"}]},
            {"time": "1800", "tempC": "24", "chanceofrain": "80", "weatherDesc": [{"value": "雨"}]},
        ],
    }],
}


def test_get_weather_returns_expected_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = _MOCK_DATA

    with patch("weather.requests.get", return_value=mock_resp):
        result = get_weather()

    assert result["desc"] == "晴れ"
    assert result["temp"] == "22"
    assert result["temp_max"] == "28"
    assert result["temp_min"] == "18"
    assert result["precip_prob"] == 80
    assert result["url"] == "https://wttr.in/Nagoya"
    assert result["hourly_summary"] == [
        {"label": "朝", "time": "06:00", "temp": "22", "rain": 10, "desc": "晴れ"},
        {"label": "昼", "time": "12:00", "temp": "26", "rain": 30, "desc": "曇り"},
        {"label": "夜", "time": "18:00", "temp": "24", "rain": 80, "desc": "雨"},
    ]


def test_get_weather_uses_max_precip():
    data = {
        "current_condition": [{"temp_C": "15", "weatherDesc": [{"value": "曇り"}]}],
        "weather": [{
            "maxtempC": "20",
            "mintempC": "10",
            "hourly": [{"chanceofrain": "50"}, {"chanceofrain": "80"}, {"chanceofrain": "20"}],
        }],
    }
    mock_resp = Mock()
    mock_resp.json.return_value = data

    with patch("weather.requests.get", return_value=mock_resp):
        result = get_weather()

    assert result["precip_prob"] == 80


def test_get_weather_raises_on_http_error():
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = Exception("HTTP 500")

    with patch("weather.requests.get", return_value=mock_resp):
        with pytest.raises(Exception):
            get_weather()


def test_get_weather_hourly_summary_empty_when_no_target_slots():
    data = {
        "current_condition": [{"temp_C": "20", "weatherDesc": [{"value": "晴れ"}]}],
        "weather": [{
            "maxtempC": "25",
            "mintempC": "15",
            "hourly": [
                {"time": "300",  "tempC": "19", "chanceofrain": "5",  "weatherDesc": [{"value": "晴れ"}]},
                {"time": "900",  "tempC": "21", "chanceofrain": "10", "weatherDesc": [{"value": "晴れ"}]},
                {"time": "1500", "tempC": "24", "chanceofrain": "20", "weatherDesc": [{"value": "曇り"}]},
            ],
        }],
    }
    mock_resp = Mock()
    mock_resp.json.return_value = data

    with patch("weather.requests.get", return_value=mock_resp):
        result = get_weather()

    assert result["hourly_summary"] == []
