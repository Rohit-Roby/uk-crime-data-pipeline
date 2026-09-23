import pytest
from transform import clean_crime_record, clean_records
@pytest.fixture
def crime_records():
    record = {
            "valid_data": {
                    "category": "anti-social-behaviour",
                    "location_type": "Force",
                    "location": {
                        "latitude": "51.509865",
                        "longitude": "-0.118092",
                        "street": {"id": 12345, "name": "On or near High Street"},
                    },
                    "context": "",
                    "outcome_status": {
                        "category": "Investigation complete; no suspect identified",
                        "date": "2021-01",
                    },
                    "persistent_id": "",
                    "id": 123456789,
                    "location_subtype": "",
                    "month": "2021-01",
                },
                "invalid_coordinate_data": {
                    "category": "anti-social-behaviour",
                    "location_type": "Force",
                    "location": {
                        "latitude": "unknown",
                        "longitude": None,
                        "street": {"id": 12345, "name": "On or near High Street"},
                    },
                    "context": "",
                    "outcome_status": {
                        "category": "Investigation complete; no suspect identified",
                        "date": "2021-01",
                    },
                    "persistent_id": "",
                    "id": 123456789,
                    "location_subtype": "",
                    "month": "2021-01",
                },
                "missing_location_data": {
                    "id": 123456789,
                    "category": "burglary",
                    "month": "2021-01"
                },
                'empty_record': {}
            }
    return record

def test_clean_crime_record_valid_data(crime_records):

    result = clean_crime_record(crime_records['valid_data'])
    assert result['id'] == 123456789
    assert result['category'] == 'anti-social-behaviour'
    assert result['latitude'] == 51.509865
    assert result['longitude'] == -0.118092
    assert result['street'] == 'On or near High Street'
    assert result['month'] == '2021-01'

def test_clean_crime_record_invalid_coordinates(crime_records):
    result = clean_crime_record(crime_records['invalid_coordinate_data'])

    assert result['latitude'] is None
    assert result['longitude'] is None

def test_clean_crime_record_missing_location(crime_records):
    result = clean_crime_record(crime_records['missing_location_data'])

    assert result['latitude'] is None
    assert result['longitude'] is None 
    assert result['street'] is None

def test_clean_crime_record_empty_record(crime_records):
    result = clean_crime_record(crime_records['empty_record'])

    assert result['id'] is None
    assert result['category'] is None
    assert result['latitude'] is None
    assert result['longitude'] is None
    assert result['street'] is None
    assert result['month'] is None

def test_clean_records_with_mixed_data(crime_records):
    mixed_data = [
        crime_records['valid_data'],
        crime_records['invalid_coordinate_data'],
        crime_records['missing_location_data'],
        crime_records['empty_record']
    ]

    cleaned_data = clean_records(mixed_data)

    assert len(cleaned_data) == 4
    assert cleaned_data[0]['latitude'] == 51.509865
    assert cleaned_data[1]['latitude'] is None
    assert cleaned_data[2]['latitude'] is None
    assert cleaned_data[3]['latitude'] is None