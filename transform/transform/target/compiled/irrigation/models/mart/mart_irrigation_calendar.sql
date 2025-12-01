

with base as (
    select
        date::date                         as calendar_date,
        -- TODO: remplacer par un vrai region_key plus tard
        'default_region'::text             as region_key,
        tavg,
        tmin,
        tmax,
        prcp,
        prcp_7d,
        tavg_7d,
        is_dry_day,
        is_hot_day,
        should_irrigate
    from "irrigation"."main"."mart_weather_features"
),

with_window as (
    select
        calendar_date,
        region_key,
        tavg,
        tmin,
        tmax,
        prcp,
        prcp_7d,
        tavg_7d,
        is_dry_day,
        is_hot_day,
        should_irrigate,
        -- offset relatif à aujourd'hui
        datediff('day', current_date, calendar_date) as day_offset,
        case
            when calendar_date <  current_date then 'PAST'
            when calendar_date =  current_date then 'TODAY'
            else 'FUTURE'
        end as period_type
    from base
)

select *
from with_window
where calendar_date between current_date - 7
                        and current_date + 7
order by calendar_date