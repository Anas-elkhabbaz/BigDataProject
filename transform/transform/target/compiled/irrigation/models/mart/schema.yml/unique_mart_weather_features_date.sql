
    
    

select
    date as unique_field,
    count(*) as n_records

from "irrigation"."main"."mart_weather_features"
where date is not null
group by date
having count(*) > 1


