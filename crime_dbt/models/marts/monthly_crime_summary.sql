{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'insert_overwrite',
        partition_by ={
            "field" : "crime_month",
            "data_type" : "date",
            "granularity" : "month"

        }
    )
}}

select 
    crime_month,
    category,
    count(*) as total_crimes
    
from {{ref('stg_crimes')}}

{% if is_incremental()%}

where crime_month = date('{{var("crime_month")}}')

{% endif %}

group by crime_month, category