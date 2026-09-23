import logging
logger = logging.getLogger(__name__)


def clean_records(data):
    cleaned_data = []
    missing_cordinates = 0
    for record in data:
        cleaned_record = clean_crime_record(record)

        if (cleaned_record['latitude'] is None or cleaned_record['longitude'] is None): missing_cordinates +=1 
            
        cleaned_data.append(cleaned_record)

    logger.info('Successfully cleaned %d records', len(cleaned_data))

    if missing_cordinates > 0:
        logger.warning('%d records have missing coordinates', missing_cordinates)
    return cleaned_data


def clean_crime_record(record):
    try:
        latitude = float(record["location"]["latitude"])
    except (ValueError, TypeError, KeyError):
        latitude = None

    try:
        longitude = float(record["location"]["longitude"])
    except (ValueError, TypeError, KeyError):
        longitude = None

    location = record.get('location') or {}
    street = location.get('street') or {}
    
    cleaned_record = {
        "id": record.get("id"),
        "category": record.get("category"),
        "latitude": latitude,
        "longitude": longitude,
        "street": street.get("name"),
        "month": record.get("month")
    }
    return cleaned_record