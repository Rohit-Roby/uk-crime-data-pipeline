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

monthly_history as (

    select
        crime_month,
        total_crimes,

        lag(total_crimes) over (
            order by crime_month
        ) as previous_record_month,
        lag(total_crimes) over (
            order by crime_month
        ) as previous_record_total

    from monthly_totals
)
validated_comparisons as (
    select 
        crime_month, 
        total_crimes, 
        
        case
            when date_diff(
                crime_month, previous_record_month, month
            ) = 1
            then previous_record_total
            else null
        end as previous_month_total
    from monthly_history
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