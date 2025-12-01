from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
import os

# Remplace par ton username Docker Hub
DOCKER_IMAGE = "anaselkhabbaz/irrigation-etl:latest"

default_args = {
    "owner": "anaselkhabbaz",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="meltano_irrigation_etl",
    description="Run Meltano ETL for Weather-aware Irrigation Planner",
    default_args=default_args,
    schedule_interval="@daily",  # tu peux mettre "0 2 * * *" par ex.
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["irrigation", "meltano", "duckdb"],
) as dag:

    run_meltano = DockerOperator(
        task_id="run_meltano_etl",
        image=DOCKER_IMAGE,
        api_version="auto",
        auto_remove=True,
        command="meltano --environment=dev run extract_clean_build",
        environment={
        "METEOSTAT_KEY": os.environ.get("METEOSTAT_KEY"),
        "LAT": os.environ.get("LAT"),
        "LON": os.environ.get("LON"),
        "START": os.environ.get("START"),
        "END": os.environ.get("END"),
        "TZ": os.environ.get("TZ"),
        "WEATHERAPI_KEY": os.environ.get("WEATHERAPI_KEY"),
        "LOCATION": os.environ.get("LOCATION"),
        "FORECAST_DAYS": os.environ.get("FORECAST_DAYS"),
        "MELTANO_ENVIRONMENT": "dev",
        "UV_HTTP_TIMEOUT": "120",
        },
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        # si tu as besoin de variables env spécifiques :
        mount_tmp_dir=False,
    )
