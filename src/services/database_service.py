import sqlite3
import os
import pandas as pd
import logging
from src.config.settings import PROCESSED_DIR, BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "data", "racevision.db")
logger = logging.getLogger("RaceVisionDB")

class DatabaseService:
    def __init__(self):
        self.db_path = DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        logger.info(f"Initializing SQLite database at: {self.db_path}")
        with self.get_connection() as conn:
            # 1. Prediction History Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    driver_id INTEGER,
                    driver_name TEXT,
                    constructor_id INTEGER,
                    constructor_name TEXT,
                    circuit_name TEXT,
                    grid INTEGER,
                    weather TEXT,
                    tyre_compound TEXT,
                    predicted_position INTEGER,
                    podium_probability REAL,
                    performance_score INTEGER,
                    explanation TEXT,
                    confidence REAL
                )
            """)

            # 2. Model Versions Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE,
                    regressor_algorithm TEXT,
                    classifier_algorithm TEXT,
                    features_used TEXT,
                    is_active INTEGER,
                    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Evaluation Metrics Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_version TEXT,
                    algorithm TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    FOREIGN KEY (model_version) REFERENCES model_versions(version)
                )
            """)

            # 4. Driver Statistics Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS driver_statistics (
                    driver_id INTEGER PRIMARY KEY,
                    driver_name TEXT,
                    nationality TEXT,
                    driver_age REAL,
                    driver_experience INTEGER,
                    driver_recent_form REAL,
                    driver_rolling_grid REAL,
                    driver_avg_finish REAL,
                    driver_consistency REAL,
                    driver_win_rate REAL,
                    driver_podium_rate REAL,
                    driver_top10_rate REAL,
                    driver_dnf_rate REAL
                )
            """)

            # 5. Team Statistics Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS team_statistics (
                    constructor_id INTEGER PRIMARY KEY,
                    constructor_name TEXT,
                    nationality TEXT,
                    constructor_strength_index REAL
                )
            """)
            conn.commit()

        # Seed initial datasets
        self.seed_statistics()
        self.seed_model_info()

    def seed_statistics(self):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM driver_statistics")
            if cursor.fetchone()[0] == 0:
                logger.info("Database empty. Seeding driver and team statistics from ml_ready_dataset.csv...")
                ml_ready_path = os.path.join(PROCESSED_DIR, "ml_ready_dataset.csv")
                if os.path.exists(ml_ready_path):
                    df = pd.read_csv(ml_ready_path)
                    
                    # Merge 'round' from races.csv to enable chronological sorting
                    races_path = os.path.join(PROCESSED_DIR, "races.csv")
                    if os.path.exists(races_path):
                        races_df = pd.read_csv(races_path)
                        df = df.merge(races_df[['race_id', 'round']], on='race_id', how='left')
                    else:
                        df['round'] = 0
                    
                    # Merge driver nationality from drivers.csv
                    drivers_path = os.path.join(PROCESSED_DIR, "drivers.csv")
                    if os.path.exists(drivers_path):
                        drivers_df = pd.read_csv(drivers_path)
                        drivers_df = drivers_df.rename(columns={'nationality': 'driver_nationality'})
                        df = df.merge(drivers_df[['driver_id', 'driver_nationality']], on='driver_id', how='left')
                    else:
                        df['driver_nationality'] = 'Unknown'
                        
                    # Merge constructor nationality from constructors.csv
                    constructors_path = os.path.join(PROCESSED_DIR, "constructors.csv")
                    if os.path.exists(constructors_path):
                        constructors_df = pd.read_csv(constructors_path)
                        constructors_df = constructors_df.rename(columns={'nationality': 'constructor_nationality'})
                        df = df.merge(constructors_df[['constructor_id', 'constructor_nationality']], on='constructor_id', how='left')
                    else:
                        df['constructor_nationality'] = 'Unknown'

                    # Sort chronologically to get the most recent data row per driver/team
                    df = df.sort_values(by=['year', 'round'])
                    
                    # Group by driver_id and take last row
                    latest_drivers = df.groupby('driver_id').last().reset_index()
                    driver_rows = []
                    for _, r in latest_drivers.iterrows():
                        driver_rows.append((
                            int(r['driver_id']),
                            str(r['driver_name']),
                            str(r['driver_nationality']),
                            float(r['driver_age']),
                            int(r['driver_experience']),
                            float(r['driver_recent_form']),
                            float(r['driver_rolling_grid']),
                            float(r['driver_avg_finish']),
                            float(r['driver_consistency']),
                            float(r['driver_win_rate']),
                            float(r['driver_podium_rate']),
                            float(r['driver_top10_rate']),
                            float(r['driver_dnf_rate'])
                        ))
                    
                    conn.executemany("""
                        INSERT OR REPLACE INTO driver_statistics (
                            driver_id, driver_name, nationality, driver_age, driver_experience,
                            driver_recent_form, driver_rolling_grid, driver_avg_finish, driver_consistency,
                            driver_win_rate, driver_podium_rate, driver_top10_rate, driver_dnf_rate
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, driver_rows)
                    
                    # Populate team statistics
                    latest_constructors = df.groupby('constructor_id').last().reset_index()
                    constructor_rows = []
                    for _, r in latest_constructors.iterrows():
                        constructor_rows.append((
                            int(r['constructor_id']),
                            str(r['constructor_name']),
                            str(r['constructor_nationality']),
                            float(r['constructor_strength_index'])
                        ))
                    conn.executemany("""
                        INSERT OR REPLACE INTO team_statistics (
                            constructor_id, constructor_name, nationality, constructor_strength_index
                        ) VALUES (?, ?, ?, ?)
                    """, constructor_rows)
                    conn.commit()
                    logger.info("Successfully seeded statistics tables.")
                else:
                    logger.warning("ml_ready_dataset.csv not found. Could not seed database statistics.")

    def seed_model_info(self):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM model_versions")
            if cursor.fetchone()[0] == 0:
                logger.info("Seeding model versions and comparison metrics...")
                conn.execute("""
                    INSERT OR REPLACE INTO model_versions (version, regressor_algorithm, classifier_algorithm, features_used, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "v1.0.0",
                    "ExtraTreesRegressor",
                    "RandomForestClassifier",
                    "grid,driver_age,driver_experience,driver_recent_form,driver_rolling_grid,driver_avg_finish,driver_consistency,driver_win_rate,driver_podium_rate,driver_top10_rate,driver_dnf_rate,grid_delta_to_avg,constructor_strength_index,circuit_familiarity,circuit_grid_importance,is_home_race",
                    1
                ))
                
                # Seed regression comparisons
                reg_csv = os.path.join(BASE_DIR, "reports", "regression_comparison.csv")
                if os.path.exists(reg_csv):
                    df_reg = pd.read_csv(reg_csv)
                    for _, r in df_reg.iterrows():
                        alg = str(r['Algorithm'])
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "MAE", float(r['MAE'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "RMSE", float(r['RMSE'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "R2", float(r['R2 Score'])))
                
                # Seed classification comparisons
                clf_csv = os.path.join(BASE_DIR, "reports", "classification_comparison.csv")
                if os.path.exists(clf_csv):
                    df_clf = pd.read_csv(clf_csv)
                    for _, r in df_clf.iterrows():
                        alg = str(r['Algorithm'])
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "Accuracy", float(r['Accuracy'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "Precision", float(r['Precision'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "Recall", float(r['Recall'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "F1", float(r['F1 Score'])))
                        conn.execute("INSERT INTO evaluation_metrics (model_version, algorithm, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                                     ("v1.0.0", alg, "ROC-AUC", float(r['ROC-AUC'])))
                conn.commit()
                logger.info("Successfully seeded model versions and comparison metrics.")

    def log_prediction(self, driver_id: int, driver_name: str, constructor_id: int, constructor_name: str,
                       circuit_name: str, grid: int, weather: str, tyre_compound: str,
                       predicted_position: int, podium_probability: float, performance_score: int,
                       explanation: str, confidence: float):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO prediction_history (
                    driver_id, driver_name, constructor_id, constructor_name, circuit_name,
                    grid, weather, tyre_compound, predicted_position, podium_probability,
                    performance_score, explanation, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                driver_id, driver_name, constructor_id, constructor_name, circuit_name,
                grid, weather, tyre_compound, predicted_position, podium_probability,
                performance_score, explanation, confidence
            ))
            conn.commit()

    def get_prediction_history(self, limit: int = 50):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM prediction_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_driver_statistics(self, driver_id: int):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM driver_statistics WHERE driver_id = ?", (driver_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_team_statistics(self, constructor_id: int):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM team_statistics WHERE constructor_id = ?", (constructor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_metrics_comparison(self):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT algorithm, metric_name, metric_value 
                FROM evaluation_metrics
            """)
            rows = cursor.fetchall()
            
            comparison = {}
            for row in rows:
                alg = row['algorithm']
                metric_name = row['metric_name']
                metric_val = row['metric_value']
                if alg not in comparison:
                    comparison[alg] = {}
                comparison[alg][metric_name] = metric_val
            return comparison
