{{ config(materialized='table') }}

with d as (
  select
    date,
    tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun, lat, lon
  from {{ ref('stg_weather_daily') }}
),

feat as (
  select
    *,
    sum(coalesce(prcp, 0.0)) over(order by date rows between 6  preceding and current row)  as prcp_7d,
    sum(coalesce(prcp, 0.0)) over(order by date rows between 13 preceding and current row)  as prcp_14d,
    sum(coalesce(prcp, 0.0)) over(order by date rows between 29 preceding and current row)  as prcp_30d,
    avg(tavg)              over(order by date rows between 6  preceding and current row)    as tavg_7d,
    max(tmax)              over(order by date rows between 6  preceding and current row)    as tmax_7d,
    (coalesce(prcp, 0.0) = 0.0)                                                              as is_dry_day,
    (coalesce(tmax, -1e9) >= 32)                                                             as is_hot_day
  from d
)

select
  *,
  case when prcp_7d < 10 and tavg_7d >= 20 then true else false end as should_irrigate
from feat
order by date
