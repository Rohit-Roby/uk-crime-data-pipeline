import json
import csv
import logging
logger = logging.getLogger(__name__)

# JSON Output
def save_json(data, filename):
    with open(filename, 'w',encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    logger.info('Data successfully saved to %s', filename)

# CSV Output
def save_csv(data, filename):
    if not data:
        logger.warning('No data to save.')
        return
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    logger.info('Data successfully saved %d records to %s', len(data), filename)
