select
    id,
    category,
    latitude,
    longitude,
    street,
    crime_month
from {{source('crime_data', 'crimes_partitioned')}}