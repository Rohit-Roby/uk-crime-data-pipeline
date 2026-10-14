{{
    config(
        materialized='view'
    )
}}

with monthly_totals as (

    select
        crime_month,
        sum(total_crimes) as total_crimes

    from {{ ref('monthly_crime_summary') }}

    group by crime_month

),

with_previous_month as (

    select
        crime_month,
        total_crimes,

        lag(total_crimes) over (
            order by crime_month
        ) as previous_month_total

    from monthly_totals
)

select
    crime_month,
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

from with_previous_month