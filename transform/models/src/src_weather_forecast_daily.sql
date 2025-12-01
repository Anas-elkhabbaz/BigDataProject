-- models/src/src_weather_forecast_daily.sql

with src as (

    select
        cast(date as date)           as date,
        cast(date_epoch as bigint)   as date_epoch,
        cast(tmax_c as double)       as tmax_c,
        cast(tmin_c as double)       as tmin_c,
        cast(tavg_c as double)       as tavg_c,
        cast(precip_mm as double)    as precip_mm,
        cast(humidity as double)     as humidity,
        cast(condition as varchar)   as condition,
        cast(uv as double)           as uv
    from read_csv_auto('../raw/weather_forecast_daily.csv', header = true)

)

select *
from src
