{{ config(materialized='view') }}

-- Step 0: read from src
with base as (
  select *
  from {{ ref('src_weather_daily') }}
),

-- Step 1: robust date parsing from text
parsed as (
  select
    coalesce(
      try_cast(date as date),              -- 'YYYY-MM-DD'
      try_strptime(date, '%y-%m-%d')::date,        -- 'YY-MM-DD' -> 20YY
      try_strptime(concat('20', date), '%Y-%m-%d')::date
    ) as parsed_date,

    -- keep original text cols for numeric casting below
    tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun, lat, lon
  from base
),

-- Step 2: guard against ancient years (e.g., 0025 -> 2025)
s as (
  select
    case
      when parsed_date is not null and extract(year from parsed_date) < 1900
        then parsed_date + interval 2000 years
      else parsed_date
    end as date,

    -- your existing numeric casting (unchanged)
    try_cast(nullif(tavg,'') as double) as tavg,
    try_cast(nullif(tmin,'') as double) as tmin,
    try_cast(nullif(tmax,'') as double) as tmax,
    try_cast(nullif(prcp,'') as double) as prcp,
    try_cast(nullif(snow,'') as double) as snow,
    try_cast(nullif(wdir,'') as double) as wdir,
    try_cast(nullif(wspd,'') as double) as wspd,
    try_cast(nullif(wpgt,'') as double) as wpgt,
    try_cast(nullif(pres,'') as double) as pres,
    try_cast(nullif(tsun,'') as double) as tsun,
    try_cast(nullif(lat,'')  as double) as lat,
    try_cast(nullif(lon,'')  as double) as lon
  from parsed
)

select *
from s
where date is not null
