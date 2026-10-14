{{
    config(
        materialized='view'
    )
}}

select
    crime_month,
    street,
    round(avg(latitude), 5) as latitude,
    round(avg(longitude), 5) as longitude,
    count(*) as total_crimes

from {{ ref('stg_crimes') }}

where
    street is not null
    and latitude is not null
    and longitude is not null

group by
    crime_month,
    street