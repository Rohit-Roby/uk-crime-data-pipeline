import json
import csv
from load import save_json
from load import save_csv
data = [{
        "id": 123,
        "category": "burglary",
        "latitude": 51.5
    },
    {
        "id": 456,
        "category": "vehicle-crime",
        "latitude": 52.1
    }]

def test_save_json(tmp_path):
    file_path = tmp_path/ 'test_data.json'

    save_json(data, file_path)

    assert file_path.exists()

    with open(file_path, 'r', encoding='utf-8') as file:
        saved_data = json.load(file)
    assert saved_data == data


def test_save_csv(tmp_path):
    file_path = tmp_path/ 'test_data.csv'

    save_csv(data,file_path)
    assert file_path.exists()

    with open(file_path, 'r', newline='', encoding='utf-8')as file:
        reader = csv.DictReader(file)
        saved_data = list(reader)

    assert len(saved_data) == len(data)
    assert saved_data[0]['category'] == 'burglary'
    assert float(saved_data[1]['latitude']) == 52.1

def test_save_csv_empty_data(tmp_path, caplog):
    file_path = tmp_path/ 'empty.csv'
    save_csv([], file_path)

    assert not file_path.exists()
    assert 'No data to save' in caplog.text