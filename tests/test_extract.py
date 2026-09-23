import requests
from extract import fetch_crime_data
from unittest.mock import patch, MagicMock


def test_fetch_crime_data_success():
    fake_data = [
        {
            "id": 123,
            "category": "burglary"
        },
        {
            "id": 456,
            "category": "vehicle-crime"
        }
    ]
     
    mock_response = MagicMock()
    mock_response.json.return_value = fake_data
    # mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None  # No exception for successful response

    with patch(
        'extract.requests.get', return_value=mock_response
    ) as mock_get:
            result = fetch_crime_data('http://fakeurl.com', {'date': '2021-01'})

    assert result == fake_data

    mock_get.assert_called_once_with(
        'http://fakeurl.com', params={'date': '2021-01'}, timeout=10
    )

def test_fetch_crime_data_timeout(caplog):

    with patch(
        'extract.requests.get', side_effect=requests.exceptions.Timeout
    ):
        result = fetch_crime_data('http://fakeurl.com', {'date': '2021-01'})

    assert result == []
    assert 'timed out' in caplog.text

def test_fetch_crime_data_http_error(caplog):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('500 Server Error')

    with patch(
        'extract.requests.get', return_value=mock_response
    ):
        result = fetch_crime_data('http://fakeurl.com', {'date': '2021-01'})

    assert result == []
    assert 'HTTP error' in caplog.text

def test_fetch_crime_data_connection_error(caplog):
   

    with patch(
          'extract.requests.get', side_effect = requests.exceptions.ConnectionError
     ):
          result = fetch_crime_data('http://fakeurl.com', {'date': '2021-01'})
    assert result == []
    assert 'Connection Error' in caplog.text