select 
    crime_month, 
    category, 
    total_crimes

from {{ref('monthly_crime_summary')}}
where total_crimes <= 0