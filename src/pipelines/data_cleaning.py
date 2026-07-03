import os
import sys
import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data_cleaning.log"), mode='w')
    ]
)
logger = logging.getLogger("DataCleaning")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Ensure output directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_lap_time_to_seconds(time_str: Any) -> Optional[float]:
    """
    Parses F1 lap/pit-stop time strings (e.g. '1:24.320', '58.911') into float seconds.
    Handles Ergast null string '\\N' and NaN values.
    """
    if pd.isna(time_str) or not isinstance(time_str, str) or time_str.strip() in (r'\N', ''):
        return None
    try:
        time_str = time_str.strip()
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except (ValueError, IndexError) as e:
        logger.debug(f"Failed to parse time string '{time_str}': {e}")
        return None

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names to lowercase and snake_case.
    """
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.replace(r'(?<!^)(?=[A-Z])', '_', regex=True) # camelCase to snake_case
        .str.lower()
        .str.replace('__', '_')
    )
    return df

def analyze_raw_table(df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
    """
    Analyzes a single raw DataFrame and computes key quality metrics.
    Treats '\\N' as a missing/null value.
    """
    total_rows = len(df)
    metrics = {
        "table_name": table_name,
        "total_rows": total_rows,
        "columns_count": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "columns_summary": {}
    }
    
    for col in df.columns:
        col_series = df[col]
        # Treat '\N' as null
        null_mask = col_series.isna() | (col_series.astype(str).str.strip() == r'\N')
        null_count = int(null_mask.sum())
        null_pct = float(null_count / total_rows * 100) if total_rows > 0 else 0.0
        unique_count = int(col_series[~null_mask].nunique())
        
        # Check data types and details
        metrics["columns_summary"][col] = {
            "dtype": str(col_series.dtype),
            "null_count": null_count,
            "null_pct": round(null_pct, 2),
            "unique_count": unique_count
        }
    return metrics

class DataCleaningPipeline:
    def __init__(self, raw_dir: str, processed_dir: str):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.quality_report: Dict[str, Any] = {}
        self.cleaning_summary: List[Dict[str, Any]] = []

    def load_raw_table(self, file_name: str) -> pd.DataFrame:
        path = os.path.join(self.raw_dir, file_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raw data file not found: {path}")
            
        if file_name == "races.csv":
            # Override headers since raw file has a mismatch: 8 headers vs 18 data columns
            RACES_COLUMNS = [
                "raceId", "year", "round", "circuitId", "name", "date", "time", "url",
                "fp1_date", "fp1_time", "fp2_date", "fp2_time", "fp3_date", "fp3_time",
                "quali_date", "quali_time", "sprint_date", "sprint_time"
            ]
            return pd.read_csv(path, header=0, names=RACES_COLUMNS)
            
        return pd.read_csv(path)

    def save_processed_table(self, df: pd.DataFrame, file_name: str) -> None:
        path = os.path.join(self.processed_dir, file_name)
        df.to_csv(path, index=False)
        logger.info(f"Saved cleaned table to {path} (Rows: {len(df)})")

    def run(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        logger.info("Initializing Data Cleaning Pipeline...")
        
        # 1. Circuits
        self.clean_circuits()
        
        # 2. Constructors
        self.clean_constructors()
        
        # 3. Drivers
        self.clean_drivers()
        
        # 4. Races
        self.clean_races()
        
        # 5. Results
        self.clean_results()
        
        # 6. Status
        self.clean_status()
        
        # 7. Qualifying
        self.clean_qualifying()
        
        # 8. Lap Times
        self.clean_lap_times()
        
        # 9. Pit Stops
        self.clean_pit_stops()
        
        # 10. Standings (Driver & Constructor)
        self.clean_standings()
        
        logger.info("Data Cleaning Pipeline completed successfully!")
        return self.quality_report, self.cleaning_summary

    def clean_circuits(self) -> None:
        df = self.load_raw_table("circuits.csv")
        self.quality_report["circuits"] = analyze_raw_table(df, "circuits")
        
        # Standardize columns
        df_clean = standardize_columns(df)
        
        # Clean altitude: replace '\N' with NaN, convert to float, fill missing with median
        df_clean['alt'] = df_clean['alt'].replace(r'\N', np.nan)
        df_clean['alt'] = pd.to_numeric(df_clean['alt'], errors='coerce')
        median_alt = df_clean['alt'].median()
        if pd.isna(median_alt):
            median_alt = 0.0
        df_clean['alt'] = df_clean['alt'].fillna(median_alt)
        
        # Ensure correct types
        df_clean['circuit_id'] = df_clean['circuit_id'].astype(int)
        df_clean['lat'] = df_clean['lat'].astype(float)
        df_clean['lng'] = df_clean['lng'].astype(float)
        
        # Remove duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['circuit_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "circuits.csv")
        self.cleaning_summary.append({
            "table": "circuits",
            "cleaning_steps": [
                "Standardized column names to snake_case",
                "Replaced '\\N' in 'alt' with NaN and cast to float",
                f"Imputed missing altitude values with median ({median_alt}m)",
                f"Removed {dups_removed} duplicate circuits"
            ]
        })

    def clean_constructors(self) -> None:
        df = self.load_raw_table("constructors.csv")
        self.quality_report["constructors"] = analyze_raw_table(df, "constructors")
        
        df_clean = standardize_columns(df)
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['constructor_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "constructors.csv")
        self.cleaning_summary.append({
            "table": "constructors",
            "cleaning_steps": [
                "Standardized column names",
                f"Removed {dups_removed} duplicate constructors"
            ]
        })

    def clean_drivers(self) -> None:
        df = self.load_raw_table("drivers.csv")
        self.quality_report["drivers"] = analyze_raw_table(df, "drivers")
        
        df_clean = standardize_columns(df)
        
        # Replace '\N' with NaN or nullable values
        df_clean['number'] = df_clean['number'].replace(r'\N', np.nan)
        df_clean['number'] = pd.to_numeric(df_clean['number'], errors='coerce').astype('Int64') # Nullable Int
        
        df_clean['code'] = df_clean['code'].replace(r'\N', np.nan)
        
        # Parse date of birth
        df_clean['dob'] = pd.to_datetime(df_clean['dob'], errors='coerce')
        
        # Concatenate forename and surname for utility
        df_clean['driver_name'] = df_clean['forename'].str.strip() + " " + df_clean['surname'].str.strip()
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['driver_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "drivers.csv")
        self.cleaning_summary.append({
            "table": "drivers",
            "cleaning_steps": [
                "Standardized column names",
                "Converted driver 'number' to nullable Int64",
                "Parsed 'dob' to datetime format",
                "Created composite 'driver_name' column",
                f"Removed {dups_removed} duplicate drivers"
            ]
        })

    def clean_races(self) -> None:
        df = self.load_raw_table("races.csv")
        self.quality_report["races"] = analyze_raw_table(df, "races")
        
        df_clean = standardize_columns(df)
        
        # Convert date to datetime
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
        
        # Standardize time: combine date & time
        df_clean['time'] = df_clean['time'].replace(r'\N', np.nan)
        
        # Merge date and time only where date is not null
        date_series = df_clean['date'].dt.strftime('%Y-%m-%d')
        time_series = df_clean['time'].fillna('00:00:00')
        combined_race_time = date_series + ' ' + time_series
        df_clean['race_timestamp'] = pd.to_datetime(combined_race_time, errors='coerce')
        
        # Clean weekend session times (fp1, fp2, fp3, quali, sprint)
        session_cols = ['fp1', 'fp2', 'fp3', 'quali', 'sprint']
        for col in session_cols:
            date_col = f"{col}_date"
            time_col = f"{col}_time"
            if date_col in df_clean.columns and time_col in df_clean.columns:
                df_clean[date_col] = df_clean[date_col].replace(r'\N', np.nan)
                df_clean[time_col] = df_clean[time_col].replace(r'\N', np.nan)
                
                # Combine only when date is present, otherwise set to NaT
                date_series_session = df_clean[date_col]
                time_series_session = df_clean[time_col].fillna('00:00:00')
                
                combined_series = pd.Series(index=df_clean.index, dtype='object')
                valid_mask = date_series_session.notna()
                combined_series.loc[valid_mask] = date_series_session.loc[valid_mask] + ' ' + time_series_session.loc[valid_mask]
                
                df_clean[f"{col}_timestamp"] = pd.to_datetime(combined_series, errors='coerce')
                df_clean.drop(columns=[date_col, time_col], inplace=True)
                
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['race_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "races.csv")
        self.cleaning_summary.append({
            "table": "races",
            "cleaning_steps": [
                "Standardized column names",
                "Fixed header mismatch (overrode 8-column header with correct 18 columns)",
                "Converted 'date' to datetime object",
                "Merged 'date' and 'time' into 'race_timestamp'",
                "Cleaned sub-sessions (fp1, fp2, fp3, quali, sprint) dates/times and consolidated them into timestamps",
                f"Removed {dups_removed} duplicate races"
            ]
        })

    def clean_results(self) -> None:
        df = self.load_raw_table("results.csv")
        self.quality_report["results"] = analyze_raw_table(df, "results")
        
        df_clean = standardize_columns(df)
        
        # Replace '\N' with NaN across columns
        cols_to_nan = ['position', 'milliseconds', 'fastest_lap', 'rank', 'fastest_lap_time', 'fastest_lap_speed']
        for col in cols_to_nan:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].replace(r'\N', np.nan)
                
        # Cast to proper types
        df_clean['position'] = pd.to_numeric(df_clean['position'], errors='coerce').astype('Int64')
        df_clean['milliseconds'] = pd.to_numeric(df_clean['milliseconds'], errors='coerce').astype('Int64')
        df_clean['fastest_lap'] = pd.to_numeric(df_clean['fastest_lap'], errors='coerce').astype('Int64')
        df_clean['rank'] = pd.to_numeric(df_clean['rank'], errors='coerce').astype('Int64')
        df_clean['fastest_lap_speed'] = pd.to_numeric(df_clean['fastest_lap_speed'], errors='coerce').astype(float)
        
        # Convert fastest lap time string to seconds
        df_clean['fastest_lap_time_seconds'] = df_clean['fastest_lap_time'].apply(parse_lap_time_to_seconds)
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['result_id'])
        dups_removed = initial_len - len(df_clean)
        
        # Outlier Detection: Identify races with anomalously long or short average/winning milliseconds.
        # Cleaned milliseconds can be checked against a standard race duration (e.g. 500,000 to 15,000,000 ms).
        # We flag anything over 4 hours (14,400,000 ms) or under 40 mins (2,400,000 ms) for finished cars.
        finished_mask = df_clean['status_id'] == 1
        long_races = df_clean[finished_mask & (df_clean['milliseconds'] > 14400000)]
        short_races = df_clean[finished_mask & (df_clean['milliseconds'] < 2400000)]
        
        logger.info(f"Outlier Analysis for 'results': Found {len(long_races)} finished results with >4h duration (Red flag races).")
        logger.info(f"Outlier Analysis for 'results': Found {len(short_races)} finished results with <40min duration.")
        
        self.save_processed_table(df_clean, "results.csv")
        self.cleaning_summary.append({
            "table": "results",
            "cleaning_steps": [
                "Standardized column names",
                "Replaced '\\N' with NaN in results columns (position, milliseconds, fastest_lap, rank, fastest_lap_speed)",
                "Converted positions and lap counts to nullable Int64 types",
                "Converted fastest lap times (e.g. '1:24.320') to float seconds",
                f"Identified {len(long_races)} race results with abnormally long race times (>4 hours, likely red-flagged)",
                f"Removed {dups_removed} duplicate race results"
            ]
        })

    def clean_status(self) -> None:
        df = self.load_raw_table("status.csv")
        self.quality_report["status"] = analyze_raw_table(df, "status")
        
        df_clean = standardize_columns(df)
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['status_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "status.csv")
        self.cleaning_summary.append({
            "table": "status",
            "cleaning_steps": [
                "Standardized column names",
                f"Removed {dups_removed} duplicate status entries"
            ]
        })

    def clean_qualifying(self) -> None:
        df = self.load_raw_table("qualifying.csv")
        self.quality_report["qualifying"] = analyze_raw_table(df, "qualifying")
        
        df_clean = standardize_columns(df)
        
        # Replace '\N' with NaN
        for col in ['q1', 'q2', 'q3']:
            df_clean[col] = df_clean[col].replace(r'\N', np.nan)
            df_clean[f"{col}_seconds"] = df_clean[col].apply(parse_lap_time_to_seconds)
            
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['qualify_id'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "qualifying.csv")
        self.cleaning_summary.append({
            "table": "qualifying",
            "cleaning_steps": [
                "Standardized column names",
                "Replaced '\\N' in q1, q2, q3 columns with NaN",
                "Parsed qualifying string lap times (Q1/Q2/Q3) to float seconds",
                f"Removed {dups_removed} duplicate qualifying records"
            ]
        })

    def clean_lap_times(self) -> None:
        df = self.load_raw_table("lap_times.csv")
        self.quality_report["lap_times"] = analyze_raw_table(df, "lap_times")
        
        df_clean = standardize_columns(df)
        
        # Replace '\N'
        df_clean['time'] = df_clean['time'].replace(r'\N', np.nan)
        df_clean['lap_time_seconds'] = df_clean['time'].apply(parse_lap_time_to_seconds)
        
        # Type conversions
        df_clean['race_id'] = df_clean['race_id'].astype(int)
        df_clean['driver_id'] = df_clean['driver_id'].astype(int)
        df_clean['lap'] = df_clean['lap'].astype(int)
        df_clean['position'] = df_clean['position'].astype(int)
        df_clean['milliseconds'] = df_clean['milliseconds'].astype(int)
        
        # Outlier Detection: Lap times that are extremely slow (e.g. safety car, pit stops) or extremely fast (errors)
        # Standard lap times are usually between 50s and 120s. We log how many are >200s or <45s.
        extreme_slow = df_clean[df_clean['lap_time_seconds'] > 200]
        extreme_fast = df_clean[df_clean['lap_time_seconds'] < 45]
        logger.info(f"Outlier Analysis for 'lap_times': Found {len(extreme_slow)} laps >200s and {len(extreme_fast)} laps <45s.")
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['race_id', 'driver_id', 'lap'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "lap_times.csv")
        self.cleaning_summary.append({
            "table": "lap_times",
            "cleaning_steps": [
                "Standardized column names",
                "Parsed lap time string into float seconds",
                f"Identified {len(extreme_slow)} slow laps (>200s, likely safety car / red flag) and {len(extreme_fast)} fast laps (<45s, likely telemetry glitch/historic short layouts)",
                f"Removed {dups_removed} duplicate lap time entries"
            ]
        })

    def clean_pit_stops(self) -> None:
        df = self.load_raw_table("pit_stops.csv")
        self.quality_report["pit_stops"] = analyze_raw_table(df, "pit_stops")
        
        df_clean = standardize_columns(df)
        
        # Clean duration: replace '\N'
        df_clean['duration'] = df_clean['duration'].replace(r'\N', np.nan)
        df_clean['duration_seconds'] = df_clean['duration'].apply(parse_lap_time_to_seconds)
        
        # If duration_seconds is still null but milliseconds is present, compute it
        df_clean['milliseconds'] = pd.to_numeric(df_clean['milliseconds'], errors='coerce')
        df_clean['duration_seconds'] = df_clean['duration_seconds'].fillna(df_clean['milliseconds'] / 1000.0)
        
        # Outlier Detection: pit stops that took extremely long (e.g. >100 seconds)
        long_stops = df_clean[df_clean['duration_seconds'] > 100]
        logger.info(f"Outlier Analysis for 'pit_stops': Found {len(long_stops)} pit stops >100 seconds.")
        
        # Drop duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['race_id', 'driver_id', 'stop'])
        dups_removed = initial_len - len(df_clean)
        
        self.save_processed_table(df_clean, "pit_stops.csv")
        self.cleaning_summary.append({
            "table": "pit_stops",
            "cleaning_steps": [
                "Standardized column names",
                "Converted duration to float seconds and synced with milliseconds",
                f"Identified {len(long_stops)} pit stops >100s (representing car repairs or red flags)",
                f"Removed {dups_removed} duplicate pit stop records"
            ]
        })

    def clean_standings(self) -> None:
        # Driver Standings
        df_ds = self.load_raw_table("driver_standings.csv")
        self.quality_report["driver_standings"] = analyze_raw_table(df_ds, "driver_standings")
        df_ds_clean = standardize_columns(df_ds)
        df_ds_clean['points'] = df_ds_clean['points'].astype(float)
        df_ds_clean['position'] = df_ds_clean['position'].astype(int)
        df_ds_clean['wins'] = df_ds_clean['wins'].astype(int)
        
        initial_len_ds = len(df_ds_clean)
        df_ds_clean = df_ds_clean.drop_duplicates(subset=['driver_standings_id'])
        dups_ds = initial_len_ds - len(df_ds_clean)
        self.save_processed_table(df_ds_clean, "driver_standings.csv")
        
        # Constructor Standings
        df_cs = self.load_raw_table("constructor_standings.csv")
        self.quality_report["constructor_standings"] = analyze_raw_table(df_cs, "constructor_standings")
        df_cs_clean = standardize_columns(df_cs)
        df_cs_clean['points'] = df_cs_clean['points'].astype(float)
        df_cs_clean['position'] = df_cs_clean['position'].astype(int)
        df_cs_clean['wins'] = df_cs_clean['wins'].astype(int)
        
        initial_len_cs = len(df_cs_clean)
        df_cs_clean = df_cs_clean.drop_duplicates(subset=['constructor_standings_id'])
        dups_cs = initial_len_cs - len(df_cs_clean)
        self.save_processed_table(df_cs_clean, "constructor_standings.csv")
        
        self.cleaning_summary.append({
            "table": "standings",
            "cleaning_steps": [
                "Standardized columns for both driver and constructor standings",
                "Converted points to float, and position & wins to integer types",
                f"Removed {dups_ds} duplicate driver standings and {dups_cs} duplicate constructor standings"
            ]
        })

def generate_report(quality_report: Dict[str, Any], cleaning_summary: List[Dict[str, Any]]) -> str:
    """
    Generates a Markdown preprocessing and data quality report.
    """
    lines = []
    lines.append("# Data Preprocessing & Quality Report - RaceVision AI")
    lines.append("\nThis document contains a comprehensive audit of the raw motorsport datasets, detailing missing values, data inconsistencies, outliers, and the cleaning transformations applied to make the data model-ready.\n")
    
    lines.append("## 1. Data Quality Analysis (Raw Datasets)")
    lines.append("\nBelow is the summary of the raw data properties before cleaning, identifying null values (including F1-specific `\\N` placeholders) and duplicate rows:\n")
    
    # Table of high-level stats
    lines.append("| Table Name | Total Rows | Total Columns | Duplicate Rows | Null Columns (Count > 0) |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for table, info in quality_report.items():
        null_cols = []
        for col, col_info in info["columns_summary"].items():
            if col_info["null_count"] > 0:
                null_cols.append(f"{col} ({col_info['null_pct']}%)")
        null_cols_str = ", ".join(null_cols[:3]) + ("..." if len(null_cols) > 3 else "")
        if not null_cols_str:
            null_cols_str = "None"
        lines.append(f"| `{table}` | {info['total_rows']:,} | {info['columns_count']} | {info['duplicates']} | {null_cols_str} |")
        
    lines.append("\n## 2. Preprocessing & Cleaning Transformations")
    lines.append("\nEach table was processed individually through a modular cleaning pipeline. The following transformations were successfully performed:\n")
    
    for summary in cleaning_summary:
        lines.append(f"### Component: `{summary['table']}`")
        for step in summary["cleaning_steps"]:
            lines.append(f"- {step}")
        lines.append("")
        
    lines.append("## 3. Detailed Data Profiling & Type Mapping")
    for table, info in quality_report.items():
        lines.append(f"\n### Table: `{table}`")
        lines.append("| Column | Original Dtype | Unique Values | Null Count | Null % |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for col, col_info in info["columns_summary"].items():
            lines.append(f"| `{col}` | `{col_info['dtype']}` | {col_info['unique_count']:,} | {col_info['null_count']:,} | {col_info['null_pct']}% |")
            
    return "\n".join(lines)

if __name__ == "__main__":
    pipeline = DataCleaningPipeline(RAW_DIR, PROCESSED_DIR)
    quality_report, cleaning_summary = pipeline.run()
    
    report_md = generate_report(quality_report, cleaning_summary)
    
    # Write report to files
    report_path = os.path.join(BASE_DIR, "data_preprocessing_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    logger.info(f"Preprocessing and data quality report successfully saved to {report_path}")
    print("\n--- Preprocessing Successful! Report Saved. ---")
