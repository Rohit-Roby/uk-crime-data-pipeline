select 
    crime_month,
    category,
    count(*) as row_count
from {{ref('monthly_crime_summary')}}
group by crime_month, category
having count(*) > 1