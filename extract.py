import requests
import logging
logger = logging.getLogger(__name__)

def fetch_crime_data(url, params):
    try:
        logger.info('Sending request to police API')
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()  # Raise an exception for HTTP errors
        data = res.json()
        logger.info('Successfully fetched %drecords from police API', len(data))
        return data
    except requests.exceptions.HTTPError as e:
            logger.exception('HTTP error occurred: %s', e)
    except requests.exceptions.Timeout as e:
            logger.exception('Police API request timed out')
    except requests.exceptions.ConnectionError as e:
        logger.exception('Connection Error')
    except requests.exceptions.RequestException as e:
        logger.error('Error fetching data, request failed: %s', e)
    
    return []
