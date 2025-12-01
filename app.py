import duckdb
import pandas as pd
import streamlit as st
from datetime import timedelta, date

# --------------------
# CONFIG
# --------------------
DB_PATH = "warehouse/irrigation.duckdb"
TABLE_NAME = "main.mart_weather_features"        # mart de features météo
CALENDAR_TABLE = "main.mart_irrigation_calendar"  # calendrier d'irrigation

# Config Streamlit (à mettre le plus haut possible)
st.set_page_config(
    page_title="Weather-aware Irrigation Planner",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------
# HELPERS GÉNÉRAUX
# --------------------
def detect_irrigation_column(df: pd.DataFrame) -> str | None:
    """
    Essaie de trouver une colonne de conseil d'irrigation dans un dataframe.
    Cherche des noms contenant 'irrig' ou 'water'.
    """
    candidates = [c for c in df.columns if "irrig" in c.lower() or "water" in c.lower()]
    return candidates[0] if candidates else None


# --------------------
# HELPER: load data (mart_weather_features)
# --------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(f"SELECT * FROM {TABLE_NAME}").fetch_df()
    con.close()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


# --------------------
# HELPER: load calendar data (mart_irrigation_calendar)
# --------------------
@st.cache_data(show_spinner=False)
def load_calendar_data() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(f"SELECT * FROM {CALENDAR_TABLE}").fetch_df()
    con.close()

    if "calendar_date" in df.columns:
        df["calendar_date"] = pd.to_datetime(df["calendar_date"])
    return df


# --------------------
# PAGE 1: OVERVIEW
# --------------------
def page_overview(df: pd.DataFrame):
    st.title("💧 Weather-aware Irrigation Planner – Overview")

    st.markdown(
        """
Welcome to the **Weather-aware Irrigation Planner**.

This tool helps farmers and decision-makers decide **when to irrigate** based on
weather data and simple decision rules. It is built on top of a modern data stack:

- **Meltano** → orchestrates the pipeline and extracts raw weather data from APIs  
- **dbt + DuckDB** → cleans the data, creates features and computes irrigation decisions  
- **Streamlit** → provides this interactive web UI
        """
    )

    st.header("1. What is irrigation and why is timing important?")
    st.markdown(
        """
Irrigation is the process of supplying water to crops when rainfall is **not enough**.

If you irrigate:
- **Too early or too often** → you waste water, energy and money, and may damage the soil.  
- **Too late** → crops suffer from stress, yield and quality go down.

The goal is to find a **balance**: use **just enough water**, at the **right time**.
        """
    )

    st.header("2. What does this project do today (Version 1)?")
    st.markdown(
        """
Right now, the system uses **historical daily weather data** for your region:

- Temperature: `tmin`, `tmax`, `tavg`  
- Rainfall: `prcp` (mm of precipitation)  
- Other variables: wind, pressure, sunshine, etc.

From this raw data, the dbt models compute **features**, for example:

- Rolling averages of temperature (e.g. `tavg_7d`)  
- Rolling sums of rain (e.g. `prcp_7d`, `prcp_30d`)  
- Flags such as `is_dry_day`, `is_hot_day`  

Then we apply a **simple rule-based logic** to generate an **irrigation advice** column,
for example:

- `WATER_NOW` → conditions are dry/hot enough to justify irrigation  
- `DELAY` → recent or upcoming rain, better to wait  
- `NEUTRAL` → intermediate situation, no strong recommendation

These labels do **not** come from the API; they are **computed by your mart**.
        """
    )

    st.header("3. How will we optimize this with forecasting?")
    st.markdown(
        """
In the next versions, we plan to improve decisions with **forecast data**:

1. **Add a weather forecast API** (e.g. OpenWeather or Meteostat forecast)  
2. Combine **past weather** (soil memory) + **future rainfall/temperature**  
3. Define smarter rules such as:

   - *If the next 3 days have high rain probability → DELAY irrigation*  
   - *If the last 7 days are very dry AND no rain is expected → WATER_NOW*  

Later, we can even add a **machine learning model** that learns the best decision
from historical examples (e.g. soil moisture, past yields).
        """
    )

    st.header("4. How to read the Dashboard page?")
    st.markdown(
        """
On the **Dashboard** page, you will see:

- **Filters (left sidebar)**  
  - Date range  
  - Region (if available)  
  - Irrigation advice (WATER_NOW / DELAY / NEUTRAL)

- **Key indicators (cards)**  
  - Number of days in the selection  
  - How many days require **WATER_NOW**  
  - How many days suggest **DELAY**  
  - Average temperature for the chosen period

- **Charts**  
  1. **Temperature line chart** → daily and rolling average temperatures  
  2. **Precipitation area chart** → daily rain and rolling sums  
  3. **Irrigation distribution bar chart** → count of WATER_NOW / DELAY / NEUTRAL

- **Detailed table**  
  - The exact data rows used to compute the charts and indicators.

Together, these elements allow you to explain **why** the system recommends
watering or delaying on specific days.
        """
    )

    # Petit snapshot dynamique
    st.subheader("Quick snapshot from current data")
    if not df.empty:
        total_days = df["date"].nunique()
        irrigation_col = detect_irrigation_column(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total days in dataset", total_days)

        if irrigation_col:
            water_now_count = (df[irrigation_col] == "WATER_NOW").sum()
            delay_count = (df[irrigation_col] == "DELAY").sum()
            with col2:
                st.metric("Total WATER_NOW days", int(water_now_count))
            with col3:
                st.metric("Total DELAY days", int(delay_count))
        else:
            st.info("No irrigation advice column found yet in the dataset.")
    else:
        st.info("Dataset is empty.")


# --------------------
# PAGE 2: DASHBOARD
# --------------------
def page_dashboard(df: pd.DataFrame):
    st.title("📊 Weather & Irrigation Dashboard")

    st.markdown(
        """
This page lets you **explore the historical data** in detail and understand  
*why* the system recommends irrigation or delay on certain days.

- Use the filters on the left to change the period or focus on specific advice.  
- If you only want a **simple answer for the coming days**, go to **“Farmer View”**
  in the navigation sidebar.
        """
    )

    if df.empty:
        st.warning("No data found in the mart table. Check your dbt pipeline.")
        return

    # --------------------
    # SIDEBAR FILTERS
    # --------------------
    st.sidebar.header("Filters")

    # Date range
    min_date = df["date"].min()
    max_date = df["date"].max()

    default_start = max_date - timedelta(days=30)  # last 30 days by default
    start_date, end_date = st.sidebar.date_input(
        "Date range",
        value=(default_start.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    # Region filter (if region column exists)
    region_col_candidates = [
        c for c in df.columns if "region" in c.lower() or "location" in c.lower()
    ]
    region_col = region_col_candidates[0] if region_col_candidates else None

    if region_col:
        regions = sorted(df[region_col].dropna().unique().tolist())
        selected_regions = st.sidebar.multiselect(
            "Region",
            options=regions,
            default=regions,  # all by default
        )
    else:
        selected_regions = None

    # Irrigation status filter
    irrigation_col = detect_irrigation_column(df)
    irrigation_options = (
        sorted(df[irrigation_col].dropna().unique().tolist())
        if irrigation_col
        else []
    )

    selected_irrigation = st.sidebar.multiselect(
        "Irrigation advice",
        options=irrigation_options,
        default=irrigation_options,
    )

    # --------------------
    # APPLY FILTERS
    # --------------------
    mask_date = (
        (df["date"] >= pd.to_datetime(start_date))
        & (df["date"] <= pd.to_datetime(end_date))
    )
    filtered_df = df.loc[mask_date].copy()

    if region_col and selected_regions:
        filtered_df = filtered_df[filtered_df[region_col].isin(selected_regions)]

    if irrigation_col and selected_irrigation:
        filtered_df = filtered_df[filtered_df[irrigation_col].isin(selected_irrigation)]

    if filtered_df.empty:
        st.warning("No data for the selected filters.")
        return

    # --------------------
    # KPIs
    # --------------------
    st.subheader("Key indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Days in selection", int(filtered_df["date"].nunique()))

    if irrigation_col:
        water_now_count = (filtered_df[irrigation_col] == "WATER_NOW").sum()
        delay_count = (filtered_df[irrigation_col] == "DELAY").sum()
    else:
        water_now_count = delay_count = 0

    with col2:
        st.metric("Days WATER_NOW", int(water_now_count))

    with col3:
        st.metric("Days DELAY", int(delay_count))

    temp_cols = [c for c in filtered_df.columns if "tavg" in c.lower()]
    avg_temp = filtered_df[temp_cols[0]].mean() if temp_cols else None

    with col4:
        if avg_temp is not None:
            st.metric("Average temperature (°C)", round(avg_temp, 1))
        else:
            st.write("No temp column found")

    # --------------------
    # CHARTS
    # --------------------
    st.subheader("Weather & Irrigation over time")

    filtered_df = filtered_df.sort_values("date")

    # Temperature chart
    st.markdown("**Temperature and rolling average**")
    temp_plot_cols = [c for c in filtered_df.columns if "tavg" in c.lower()]
    if len(temp_plot_cols) >= 1:
        temp_df = filtered_df[["date"] + temp_plot_cols].set_index("date")
        st.line_chart(temp_df)
    else:
        st.info("No temperature columns (tavg) found for plotting.")

    # Precipitation chart
    st.markdown("**Daily precipitation and rolling sum**")
    prcp_cols = [c for c in filtered_df.columns if "prcp" in c.lower()]
    if len(prcp_cols) >= 1:
        prcp_df = filtered_df[["date"] + prcp_cols].set_index("date")
        st.area_chart(prcp_df)
    else:
        st.info("No precipitation columns (prcp) found for plotting.")

    # Irrigation distribution
    if irrigation_col:
        st.markdown("**Irrigation advice distribution**")
        irr_counts = filtered_df[irrigation_col].value_counts().reset_index()
        irr_counts.columns = [irrigation_col, "count"]
        st.bar_chart(irr_counts.set_index(irrigation_col))
    else:
        st.info("No irrigation advice column found for distribution chart.")

    # --------------------
    # DATA TABLE
    # --------------------
    st.subheader("Detailed data")
    st.dataframe(filtered_df, use_container_width=True)


# --------------------
# PAGE 3: FARMER VIEW (NEXT 7 DAYS)
# --------------------
def page_farmer_view(df_calendar: pd.DataFrame):
    st.title("🚜 Farmer View – Next 7 Days")

    st.markdown(
        """
This page is a **very simple view for farmers**.

It answers one question:

> **“Today and for the next 7 days, what should I do?”**

The system uses the `mart_irrigation_calendar` table, which combines:
- past weather (soil memory),
- current day,
- and the upcoming days.
        """
    )

    if df_calendar.empty:
        st.warning("No data found in mart_irrigation_calendar. Run your dbt models first.")
        return

    if "day_offset" not in df_calendar.columns:
        st.error("Column 'day_offset' is missing in mart_irrigation_calendar.")
        return

    # Keep only today + next 7 days
    df_ = df_calendar.copy()
    df_ = df_[df_["day_offset"].between(0, 7)].sort_values("calendar_date")

    if df_.empty:
        st.info("No rows for today + next 7 days. Check your calendar model.")
        return

    has_should = "should_irrigate" in df_.columns
    has_prcp = "prcp" in df_.columns

    # Build a simple human-readable advice column
    def compute_advice(row: pd.Series) -> str:
        # règle simple, à raffiner plus tard
        if has_should and bool(row["should_irrigate"]):
            return "WATER_NOW"
        if has_prcp and pd.notna(row["prcp"]) and row["prcp"] > 0:
            return "DELAY (rain expected)"
        return "NEUTRAL"

    df_["irrigation_advice"] = df_.apply(compute_advice, axis=1)

    st.subheader("Summary for today and the next 7 days")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Days shown", len(df_))
    with col2:
        st.metric("Days WATER_NOW", int((df_["irrigation_advice"] == "WATER_NOW").sum()))
    with col3:
        st.metric("Days with rain", int((has_prcp and (df_["prcp"] > 0).sum()) or 0))

    st.markdown("### Calendar view")
    cols_to_show = ["calendar_date", "tavg", "prcp", "irrigation_advice"]
    cols_to_show = [c for c in cols_to_show if c in df_.columns]

    st.dataframe(
        df_[cols_to_show],
        use_container_width=True,
    )

    st.markdown(
        """
**How to read this table:**

- **calendar_date** → the day in the calendar  
- **tavg** → average temperature for that day (°C)  
- **prcp** → expected precipitation (mm)  
- **irrigation_advice** → what the system recommends:
  - `WATER_NOW` → conditions are dry/hot, irrigation recommended  
  - `DELAY (rain expected)` → rain is coming, better to wait  
  - `NEUTRAL` → no strong signal either way
        """
    )


# --------------------
# MAIN APP ROUTER
# --------------------
def main():
    # Navigation in the sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Dashboard", "Farmer View"])

    # Load data once (cache)
    df = load_data()
    df_calendar = load_calendar_data()

    # Route to selected page
    if page == "Overview":
        page_overview(df)
    elif page == "Dashboard":
        page_dashboard(df)
    else:
        page_farmer_view(df_calendar)


if __name__ == "__main__":
    main()
