# 🌦️ Irrigation Decision Support System

Automated weather data pipeline for smart irrigation recommendations in Casablanca, Morocco.

## 📋 Prerequisites

- **Python 3.11** or higher
- **Git** (optional, for cloning)
- **RapidAPI Account** (free tier works) - [Sign up here](https://rapidapi.com/meteostat/api/meteostat)

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd irrigation
```

### 2. Set Up Python Environment

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

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install meltano
meltano install
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Meteostat API key
# Get one from: https://rapidapi.com/meteostat/api/meteostat
```

**Edit `.env`:**
```bash
METEOSTAT_KEY=your_actual_api_key_here
LAT=34.0209  # Casablanca coordinates (change if needed)
LON=-6.8416
# ... rest stays the same
```

### 5. Create Required Directories

```bash
mkdir -p raw warehouse transform/target
```

### 6. Run the Pipeline

```bash
# Extract weather data, clean it, and build analytics
meltano run extract_clean_build
```

## 📊 What It Does

1. **Extracts** daily weather data from Meteostat API (temp, precipitation, wind, etc.)
2. **Cleans** the CSV data (removes empty lines, normalizes formatting)
3. **Transforms** with dbt to create:
   - Rolling 7/14/30-day precipitation totals
   - Rolling temperature averages
   - Irrigation recommendations based on:
     - Last 7 days rainfall < 10mm AND
     - 7-day avg temperature ≥ 20°C

## 🗂️ Project Structure

```
irrigation/
├── .env                    # Your API keys (not in git!)
├── .env.example           # Template for setup
├── meltano.yml            # Pipeline configuration
├── scripts/
│   └── clean_csv.py       # CSV cleaner utility
├── raw/
│   └── weather_daily.csv  # Extracted data
├── warehouse/
│   └── irrigation.duckdb  # DuckDB database
└── transform/             # dbt project
    ├── models/
    │   ├── src/           # Source: read CSV
    │   ├── staging/       # Staging: type casting
    │   └── marts/         # Analytics: irrigation logic
    └── profiles/
        └── duckdb/
            └── profiles.yml  # Database connection
```

## 🔍 Query the Results

```bash
# Using DuckDB CLI
duckdb warehouse/irrigation.duckdb

# Example queries:
SELECT * FROM mart_weather_features 
WHERE should_irrigate = true 
ORDER BY date DESC 
LIMIT 10;

SELECT 
    date, 
    tavg_7d as avg_temp_7d,
    prcp_7d as rain_7d_mm,
    should_irrigate 
FROM mart_weather_features 
WHERE date >= '2025-10-01';
```

## 🛠️ Development

### Run Individual Steps

```bash
# Just extract data
meltano run tap-rest-api-msdk target-csv

# Just clean CSV
python scripts/clean_csv.py raw/weather_daily.csv

# Just run dbt
meltano invoke dbt-direct:run

# Run dbt tests
meltano invoke dbt-direct:test
```

### Update Date Range

Edit `.env`:
```bash
START=2024-01-01
END=2025-12-31  # Change to desired end date
```

### Change Location

Edit `.env`:
```bash
LAT=40.7128   # New York example
LON=-74.0060
TZ=America/New_York
```

## 📅 Scheduling (Optional)

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 6 AM)
4. Action: Start a program
   - Program: `C:\path\to\.venv\Scripts\python.exe`
   - Arguments: `-m meltano run extract_clean_build`
   - Start in: `C:\path\to\irrigation`

### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Run daily at 6 AM
0 6 * * * cd /path/to/irrigation && .venv/bin/meltano run extract_clean_build
```

## 🐛 Troubleshooting

### "Cannot find module 'meltano'"
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac
```

### "API rate limit exceeded"
- Free tier: 500 requests/month
- Wait or upgrade plan at RapidAPI

### "CSV parsing error"
```bash
# Manually clean CSV
python scripts/clean_csv.py raw/weather_daily.csv

# Check CSV format
head raw/weather_daily.csv
```

### dbt connection issues
```bash
# Test dbt directly
cd transform
dbt debug --profiles-dir profiles/duckdb
```

## 📚 Tech Stack

- **Meltano 4.0.5** - Data pipeline orchestration
- **dbt-core 1.8.x + dbt-duckdb** - Analytics transformations
- **DuckDB 1.3.1** - Embedded analytical database
- **tap-rest-api-msdk** - REST API extraction
- **Python 3.11** - Scripting and utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the pipeline: `meltano run extract_clean_build`
5. Submit a pull request

## 📄 License

MIT License - feel free to use for your own projects!

## 🙋 Support

Having issues? Check:
- [Meltano Docs](https://docs.meltano.com)
- [dbt-duckdb Docs](https://github.com/duckdb/dbt-duckdb)
- [Meteostat API Docs](https://dev.meteostat.net)