

with raw as (
  select *
  from read_csv('/app/raw/weather_daily.csv',
    auto_detect = false,
    header      = true,
    delim       = ',',
    quote       = '"',
    escape      = '"',
    -- Relax the parser for real-world CSVs:
    strict_mode = false,
    -- Let DuckDB read everything as text; stg will cast:
    sample_size = -1,
    ignore_errors = true,
    columns = {
      'date' : 'VARCHAR',
      'tavg' : 'VARCHAR',
      'tmin' : 'VARCHAR',
      'tmax' : 'VARCHAR',
      'prcp' : 'VARCHAR',
      'snow' : 'VARCHAR',
      'wdir' : 'VARCHAR',
      'wspd' : 'VARCHAR',
      'wpgt' : 'VARCHAR',
      'pres' : 'VARCHAR',
      'tsun' : 'VARCHAR',
      'lat'  : 'VARCHAR',
      'lon'  : 'VARCHAR'
    }
  )
)
select *
from raw
-- keep only rows that have a date value
where date is not null and trim(date) <> ''
order by date