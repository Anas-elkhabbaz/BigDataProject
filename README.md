# 🌦️ Irrigation Decision Support System

Weather-aware irrigation planner for agriculture, built as an end-to-end **data engineering pipeline**:

- Collects **historical** and **forecast** weather data
- Cleans and models the data into a **DuckDB warehouse**
- Produces a daily **irrigation calendar** using simple business rules
- Is fully **orchestrated with Airflow** and **containerised with Docker**

---

## ✨ Main Features

- 🔗 **Two data sources**
  - **Meteostat** (historical daily weather) via `tap-rest-api-msdk`
  - **WeatherAPI** (3-day forecast) via `tap-weatherapi-forecast`
- ⚙️ **Config-driven ELT** with Meltano (`meltano.yml`, `.env`, plugins/)
- 🧱 **Data warehouse** in DuckDB (`warehouse/irrigation.duckdb`)
- 🧮 **dbt models** for:
  - Sources & staging (daily + forecast)
  - Feature engineering (`mart_weather_features`)
  - Final **irrigation calendar** (`mart_irrigation_calendar`)
- 🪄 **Orchestration** with Airflow:
  - DAG: `meltano_irrigation_etl`
  - Single `DockerOperator` running `anaselkhabbaz/irrigation-etl:latest`
- 🐳 **Docker image** to run the full pipeline in a reproducible environment

---

## 🧱 Architecture Overview

High-level flow:

> APIs (Meteostat + WeatherAPI) → Meltano (Singer taps) → raw CSV  
> → `weather-tools` cleaning → dbt + DuckDB → irrigation calendar  
> → Orchestrated by Airflow (DockerOperator + Docker image)

More concretely:

1. **Meltano** runs an ELT job:
   - `tap-rest-api-msdk` calls Meteostat `/point/daily`
   - `tap-weatherapi-forecast` calls WeatherAPI `/forecast.json`
   - `target-csv` writes raw CSVs to `raw/`
   - `weather-tools` normalises the CSVs
2. **dbt-duckdb**:
   - Loads cleaned CSVs into DuckDB
   - Builds source, staging and mart models
3. **DuckDB**:
   - Stores all tables in `warehouse/irrigation.duckdb`
4. **Airflow + Docker**:
   - Airflow DAG `meltano_irrigation_etl` uses `DockerOperator`
   - Spins up `anaselkhabbaz/irrigation-etl:latest`
   - Inside the container: `meltano --environment=dev run extract_clean_build`

---

## 📋 Prerequisites

- **Python** 3.11+ (project tested on 3.13)
- **pip** ≥ 23
- **Git**
- **Docker** and **docker-compose**
- Accounts / API keys:
  - **Meteostat** (via RapidAPI)
  - **WeatherAPI.com** (free tier is enough)

---

## 🚀 Quick Start (Local – Meltano CLI)

> All commands are run from the **repository root**: `BigDataProject/`

### 1. Clone the repository

```bash
git clone https://github.com/Anas-elkhabbaz/BigDataProject.git
cd BigDataProject
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
# or at minimum:
# pip install meltano
```

Then install Meltano plugins:

```bash
meltano install
```

---

## ⚙️ Configuration (.env)

The project uses a `.env` file at the repo root to configure:

- API keys
- Location (latitude, longitude, timezone)
- Date range
- Forecast horizon

Example:

```bash
# Meteostat (via RapidAPI)
METEOSTAT_KEY=your_meteostat_key_here

# WeatherAPI.com
WEATHERAPI_KEY=your_weatherapi_key_here

# Location (example: Casablanca)
LAT=33.5731
LON=-7.5898
TZ=Africa/Casablanca

# Historical period for Meteostat
START=2024-01-01
END=2025-12-01

# Forecast horizon for WeatherAPI
FORECAST_DAYS=3
```

> Tip: you can keep a template as `.env.example` and copy it:
> `cp .env.example .env` (Linux/Mac) or `copy .env.example .env` (Windows).

---

## ▶️ Run the Full Pipeline (Local)

From the repo root, with `.venv` activated and `.env` configured:

```bash
meltano --environment=dev run extract_clean_build
```

This will:

1. Call **Meteostat** and **WeatherAPI** through singer taps
2. Write raw CSVs into `raw/` (e.g. `raw/weather_daily.csv`, `raw/weather_forecast_daily.csv`)
3. Clean them with `weather-tools`
4. Load them into **DuckDB** and build dbt models

---

## 🌐 Data Sources & Main Columns

### Meteostat – Historical daily weather

- Via `tap-rest-api-msdk`
- Endpoint `/point/daily`
- Typical columns:
  - `date`
  - `tavg`, `tmin`, `tmax`
  - `prcp` (precipitation)
  - `snow`
  - `wdir`, `wspd`
  - `pres`
  - `lat`, `lon`

### WeatherAPI – 3-day forecast

- Via `tap-weatherapi-forecast`
- Endpoint `/forecast.json`
- Typical columns:
  - `date`
  - `maxtemp_c`, `mintemp_c`, `avgtemp_c`
  - `daily_chance_of_rain`, `daily_will_it_rain`
  - `condition_text`
  - Location fields (name, region, country, tz_id)

Both are parameterized by `LAT`, `LON`, `TZ`, `START`, `END`, and `FORECAST_DAYS` from `.env`.

---

## 🧮 dbt + DuckDB Models

All dbt models live under `transform/` and target `warehouse/irrigation.duckdb`.

### Source layer (`models/src/`)

- `src_weather_daily`
- `src_weather_forecast_daily`

These read the cleaned CSVs and expose them as DuckDB tables/views.

### Staging layer (`models/staging/`)

- `stg_weather_daily`
- `stg_weather_forecast_daily`

Tasks:

- Ensure proper data types (dates, floats, booleans)
- Rename raw fields to consistent naming
- Keep only useful columns

### Mart layer (`models/marts/`)

- `mart_weather_features`
  - Rolling temperature averages (7d, 14d, 30d…)
  - Rolling rainfall sums
  - Simple indicators like `is_hot`, `is_dry`, etc.
- `mart_irrigation_calendar`
  - Final business table with one row per date:
    - Weather features
    - Forecast indicators (e.g. upcoming rain)
    - Final flag: `irrigation_need` (e.g. 0/1)
    - Optional `comment` column for interpretation

---

## 🗂️ Project Structure

*(Simplified view of the most important files)*

```text
BigDataProject/
├── airflow/
│   ├── dags/
│   │   └── meltano_irrigation_etl.py   # Airflow DAG with DockerOperator
│   └── docker-compose.yml              # Airflow stack (webserver, scheduler, etc.)
├── extract/                            # (optional) extract-related helpers
├── load/                               # (optional) load-related helpers
├── notebook/                           # Notebooks for exploration / demo
├── orchestrate/                        # Orchestration scripts / helpers
├── output/                             # Output / reports (if any)
├── plugins/                            # Meltano-managed Singer taps and utilities
├── raw/                                # Raw CSVs from taps (created at runtime)
├── scripts/
│   └── clean_csv.py                    # CSV cleaning / normalization
├── transform/                          # dbt project
│   ├── models/
│   │   ├── src/
│   │   ├── staging/
│   │   └── marts/
│   └── profiles/                       # dbt profiles for DuckDB
├── warehouse/
│   └── irrigation.duckdb              # DuckDB warehouse
├── Dockerfile                          # Docker image for the ETL
├── docker-compose.yml                  # Docker compose (can include Airflow stack)
├── meltano.yml                         # Meltano project config
├── .env.example                        # Example env config
├── app.py                              # Optional app (CLI/Streamlit) to inspect results
├── README.md                           # This file
└── requirements.txt
```

> Note: some directories are created at runtime (e.g. `raw/`, `warehouse/`).

---

## 🐳 Run with Docker & Airflow

### 1. Build the Docker image

From the repo root:

```bash
docker build -t anaselkhabbaz/irrigation-etl:latest .
```

This image:

- Includes Python + Meltano + dbt + DuckDB
- Copies the project files and `meltano.yml`
- Runs the pipeline with:
  ```bash
  meltano --environment=dev run extract_clean_build
  ```
  (triggered by Airflow’s `DockerOperator`)

### 2. Start the Airflow stack

In the `airflow/` directory (or where your Airflow `docker-compose.yml` lives):

```bash
cd airflow
docker-compose up -d
```

This will start:

- Airflow webserver (default: `http://localhost:8080`)
- Airflow scheduler
- Any supporting services (Postgres, etc., depending on `docker-compose.yml`)

### 3. Configure Airflow connections / environment

Make sure the container running `DockerOperator` can see:

- The `anaselkhabbaz/irrigation-etl:latest` image
- The `.env` file (either baked into the image or mounted as env vars)

Check `meltano_irrigation_etl` DAG to confirm:

- `image="anaselkhabbaz/irrigation-etl:latest"`
- Command calls `meltano --environment=dev run extract_clean_build`

### 4. Trigger the DAG

1. Open `http://localhost:8080`
2. Enable DAG: **`meltano_irrigation_etl`**
3. Trigger once manually (play button)
4. Check logs:
   - You should see Meltano logs like
     - `Running job dev:tap-rest-api-msdk-to-target-csv`
     - `record_count=...`
     - `dbt run summary (PASS=...)`

---

## 🔍 Querying the Warehouse

Use DuckDB CLI or any client that can connect to local DuckDB files.

```bash
duckdb warehouse/irrigation.duckdb
```

Examples:

```sql
-- Raw-like source data
SELECT * FROM main.src_weather_daily LIMIT 5;

-- Engineered features
SELECT * FROM main.mart_weather_features LIMIT 5;

-- Final irrigation calendar
SELECT
    date,
    tavg,
    prcp_last3d,
    irrigation_need,
    comment
FROM main.mart_irrigation_calendar
ORDER BY date DESC
LIMIT 10;
```

---

## 🧪 Development Commands

### Run individual Meltano steps

```bash
# Extract only (Meteostat + WeatherAPI → CSV)
meltano run tap-rest-api-msdk target-csv
meltano run tap-weatherapi-forecast target-csv

# Clean CSVs
python scripts/clean_csv.py raw/weather_daily.csv
python scripts/clean_csv.py raw/weather_forecast_daily.csv

# Build dbt models
meltano invoke dbt-duckdb:run

# Run dbt tests
meltano invoke dbt-duckdb:test
```

---

## 🐛 Troubleshooting

### Meltano / plugin install errors

- Make sure the Python venv is activated
- Run:
  ```bash
  pip install --upgrade pip
  pip install meltano
  meltano install
  ```

### API errors / rate limits

- Check your keys in `.env`:
  - `METEOSTAT_KEY`
  - `WEATHERAPI_KEY`
- Verify the quota (free plans have limits)

### CSV formatting / parsing issues

```bash
python scripts/clean_csv.py raw/weather_daily.csv
python scripts/clean_csv.py raw/weather_forecast_daily.csv
```

Then re-run:

```bash
meltano --environment=dev run extract_clean_build
```

### dbt connection errors

From `transform/`:

```bash
cd transform
dbt debug --profiles-dir profiles
```

---

## 📚 Tech Stack

- **Language:** Python 3.13
- **Orchestration:** Airflow, Docker, Docker Compose
- **Pipeline:** Meltano 4.x, Singer taps (`tap-rest-api-msdk`, `tap-weatherapi-forecast`), `target-csv`
- **Warehouse:** DuckDB 1.4.x
- **Transformations:** dbt-core 1.10.x + `dbt-duckdb`
- **Config:** `.env`, `meltano.yml`, dbt models

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally:
   ```bash
   meltano --environment=dev run extract_clean_build
   ```
5. Open a pull request

---

## 📄 License

MIT License – feel free to reuse and adapt this project.
