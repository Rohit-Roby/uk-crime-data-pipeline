{{
    config(
        materialized='view'
    )
}}

with category_history as (

    select
        crime_month,
        category,
        total_crimes,

        lag(total_crimes) over (
            partition by category
            order by crime_month
        ) as previous_month_total

    from {{ ref('monthly_crime_summary') }}

)

select
    crime_month,
    category,
    total_crimes,
    previous_month_total,

    total_crimes - previous_month_total
        as month_over_month_change,

    round(
        safe_divide(
            total_crimes - previous_month_total,
            previous_month_total
        ) * 100,
        2
    ) as month_over_month_pct_change

from category_history