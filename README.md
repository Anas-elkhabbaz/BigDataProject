# 🌦️ Irrigation Decision Support System
Smart weather-based irrigation pipeline powered by **Meltano**, **dbt-duckdb**, **DuckDB**, and **Python 3.13**.

This system automatically **extracts, cleans, transforms, and analyzes** weather data from **Meteostat** to generate actionable irrigation recommendations for agriculture.

---

## 📋 Prerequisites

- **Python 3.13** (or 3.11+)
- **Pip** ≥ 23
- **Git** (recommended)
- **Meltano 4.x** (installed via pip)
- **dbt-duckdb** plugin (installed by Meltano)
- **Meteostat REST API (via tap-rest-api-msdk)**  

---

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd BigDataProject/irrigation
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m vvenv .venv
.\.venv\Scripts\activate
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
```

Then install Meltano plugins:

```bash
meltano install
```

---

## 4. Run the Full Pipeline

```bash
meltano --environment=dev run extract_clean_build
```

---

## 📊 What the Pipeline Does

### **1. Extraction (tap-rest-api-msdk)**
Fetches:
- Temperature  
- Precipitation  
- Wind  
- Pressure  
- Sunshine  

### **2. Cleaning (clean_csv.py)**
- Normalizes dates  
- Converts dtypes  
- Removes empty/duplicate lines  

### **3. Transformation (dbt-duckdb)**
Generates:
- Rolling averages  
- Rolling rainfall  
- Irrigation index  
- Recommendation flag  

### **4. Storage (DuckDB)**

```
warehouse/irrigation.duckdb
```

---

## 🗂️ Project Structure

```
irrigation/
├── meltano.yml
├── data/
│   ├── raw/
│   └── clean/
├── scripts/
│   └── clean_csv.py
├── models/
│   ├── src/
│   ├── stg/
│   └── mart/
├── warehouse/
│   └── irrigation.duckdb
└── .venv/
```

---

## 🔍 Querying

```bash
duckdb warehouse/irrigation.duckdb
```

```sql
SELECT * FROM mart_weather_features WHERE should_irrigate = TRUE;
```

---

## 🛠️ Development

Run extraction:

```bash
meltano run tap-rest-api-msdk target-csv
```

Run cleaning:

```bash
python scripts/clean_csv.py
```

Run dbt:

```bash
meltano invoke dbt-duckdb:run
```

---

## 📅 Scheduling

### Windows Task Scheduler  
Run daily at 6 AM:

```bash
C:\path\to\.venv\Scripts\python.exe -m meltano run extract_clean_build
```

### Linux/macOS (cron):

```
0 6 * * * cd /path/to/project && .venv/bin/meltano run extract_clean_build
```

---

## 🐛 Troubleshooting

CSV errors:
```bash
python scripts/clean_csv.py
```

dbt errors:
```bash
meltano invoke dbt-duckdb:debug
```

---

## 📚 Stack
- Python 3.13  
- Meltano 4.0.5  
- tap-rest-api-msdk  
- target-csv  
- dbt-core 1.10.13  
- dbt-duckdb 1.10.0  
- DuckDB 1.4.1  

---

## 📄 License
MIT License.
