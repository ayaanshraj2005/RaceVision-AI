import os
import pandas as pd
from typing import List, Dict, Any, Optional
from src.config.settings import PROCESSED_DIR

class AnalyticsService:
    def __init__(self):
        self.drivers_path = os.path.join(PROCESSED_DIR, "drivers.csv")
        self.constructors_path = os.path.join(PROCESSED_DIR, "constructors.csv")
        self.circuits_path = os.path.join(PROCESSED_DIR, "circuits.csv")
        self.races_path = os.path.join(PROCESSED_DIR, "races.csv")
        self.results_path = os.path.join(PROCESSED_DIR, "results.csv")
        
        # Verify paths
        for path in [self.drivers_path, self.constructors_path, self.circuits_path, self.races_path, self.results_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Clean CSV file not found: {path}. Make sure to run data cleaning and eda first.")
                
        # Load datasets into memory for fast lookup
        self.drivers = pd.read_csv(self.drivers_path)
        self.constructors = pd.read_csv(self.constructors_path)
        self.circuits = pd.read_csv(self.circuits_path)
        self.races = pd.read_csv(self.races_path)
        self.results = pd.read_csv(self.results_path)
        
        # Re-index / format names to avoid column naming collisions
        self.drivers_formatted = self.drivers.rename(columns={'nationality': 'driver_nationality'})
        self.constructors_formatted = self.constructors.rename(columns={'name': 'constructor_name', 'nationality': 'constructor_nationality'})
        self.races_formatted = self.races.rename(columns={'name': 'race_name'})
        self.circuits_formatted = self.circuits.rename(columns={'name': 'circuit_name'})

    def get_dashboard_stats(self) -> Dict[str, Any]:
        total_races = len(self.races)
        total_drivers = len(self.drivers)
        total_constructors = len(self.constructors)
        total_circuits = len(self.circuits)
        seasons = sorted(self.races['year'].unique().tolist())
        
        # Calculate driver wins
        win_results = self.results[self.results['position_order'] == 1]
        driver_wins = win_results.groupby('driver_id').size().reset_index(name='wins')
        driver_wins = driver_wins.merge(self.drivers_formatted[['driver_id', 'driver_name']], on='driver_id')
        top_drivers = driver_wins.sort_values(by='wins', ascending=False).head(5).to_dict(orient='records')
        
        # Calculate constructor wins
        constructor_wins = win_results.groupby('constructor_id').size().reset_index(name='wins')
        constructor_wins = constructor_wins.merge(self.constructors_formatted[['constructor_id', 'constructor_name']], on='constructor_id')
        top_constructors = constructor_wins.sort_values(by='wins', ascending=False).head(5).to_dict(orient='records')
        
        # Clean any float NaNs in results
        top_drivers = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in top_drivers]
        top_constructors = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in top_constructors]
        
        return {
            'total_races': total_races,
            'total_drivers': total_drivers,
            'total_constructors': total_constructors,
            'total_circuits': total_circuits,
            'seasons_covered': seasons,
            'top_drivers_by_wins': top_drivers,
            'top_teams_by_wins': top_constructors
        }

    def get_drivers(self) -> List[Dict[str, Any]]:
        # Compute starts, wins, and podiums
        stats = self.results.groupby('driver_id').agg(
            total_races=('race_id', 'count'),
            wins=('position_order', lambda x: (x == 1).sum()),
            podiums=('position_order', lambda x: (x <= 3).sum())
        ).reset_index()
        
        merged = self.drivers_formatted[['driver_id', 'driver_name', 'driver_nationality', 'code', 'dob']].merge(stats, on='driver_id', how='left')
        merged = merged.fillna({'wins': 0, 'podiums': 0, 'total_races': 0})
        merged = merged.rename(columns={'driver_nationality': 'nationality'})
        
        # Replace float nan values with Python None
        records = merged.to_dict(orient='records')
        cleaned_records = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in records]
        return cleaned_records

    def get_driver_by_id(self, driver_id: int) -> Optional[Dict[str, Any]]:
        driver_row = self.drivers_formatted[self.drivers_formatted['driver_id'] == driver_id]
        if driver_row.empty:
            return None
            
        # Get driver stats
        driver_results = self.results[self.results['driver_id'] == driver_id]
        total_races = len(driver_results)
        wins = int((driver_results['position_order'] == 1).sum())
        podiums = int((driver_results['position_order'] <= 3).sum())
        
        driver_data = driver_row.iloc[0].to_dict()
        driver_data.update({
            'wins': wins,
            'podiums': podiums,
            'total_races': total_races,
            'nationality': driver_data['driver_nationality']
        })
        # Clean any float NaNs
        cleaned_data = {k: (None if pd.isna(v) else v) for k, v in driver_data.items()}
        return cleaned_data

    def get_teams(self) -> List[Dict[str, Any]]:
        stats = self.results.groupby('constructor_id').agg(
            total_races=('race_id', 'count'),
            wins=('position_order', lambda x: (x == 1).sum()),
            podiums=('position_order', lambda x: (x <= 3).sum())
        ).reset_index()
        
        merged = self.constructors_formatted[['constructor_id', 'constructor_name', 'constructor_nationality']].merge(stats, on='constructor_id', how='left')
        merged = merged.fillna({'wins': 0, 'podiums': 0, 'total_races': 0})
        merged = merged.rename(columns={'constructor_nationality': 'nationality'})
        
        records = merged.to_dict(orient='records')
        cleaned_records = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in records]
        return cleaned_records

    def get_team_by_id(self, constructor_id: int) -> Optional[Dict[str, Any]]:
        team_row = self.constructors_formatted[self.constructors_formatted['constructor_id'] == constructor_id]
        if team_row.empty:
            return None
            
        team_results = self.results[self.results['constructor_id'] == constructor_id]
        total_races = len(team_results)
        wins = int((team_results['position_order'] == 1).sum())
        podiums = int((team_results['position_order'] <= 3).sum())
        
        team_data = team_row.iloc[0].to_dict()
        team_data.update({
            'wins': wins,
            'podiums': podiums,
            'total_races': total_races,
            'nationality': team_data['constructor_nationality']
        })
        cleaned_data = {k: (None if pd.isna(v) else v) for k, v in team_data.items()}
        return cleaned_data

    def get_circuits(self) -> List[Dict[str, Any]]:
        # Count races per circuit
        races_per_circuit = self.races.groupby('circuit_id').size().reset_index(name='total_races')
        
        df_merged = self.results[['race_id', 'grid', 'position_order']].merge(self.races[['race_id', 'circuit_id']], on='race_id')
        corrs = df_merged.groupby('circuit_id')[['grid', 'position_order']].corr().iloc[0::2, -1].reset_index()
        corrs = corrs.rename(columns={'position_order': 'grid_importance_correlation'}).drop(columns=['level_1'])
        
        merged = self.circuits_formatted[['circuit_id', 'circuit_name', 'location', 'country']].merge(races_per_circuit, on='circuit_id', how='left')
        merged = merged.merge(corrs, on='circuit_id', how='left')
        merged = merged.fillna({'total_races': 0, 'grid_importance_correlation': 0.40})
        
        records = merged.to_dict(orient='records')
        cleaned_records = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in records]
        return cleaned_records

    def get_seasons(self) -> List[Dict[str, Any]]:
        # Summarize total races per season
        races_per_season = self.races.groupby('year').size().reset_index(name='total_races')
        
        # Find champions per season
        df_pts = self.results.merge(self.races[['race_id', 'year']], on='race_id')
        
        # Driver champion
        driver_season_pts = df_pts.groupby(['year', 'driver_id'])['points'].sum().reset_index()
        idx_driver_champs = driver_season_pts.groupby('year')['points'].idxmax()
        driver_champs = driver_season_pts.loc[idx_driver_champs].merge(self.drivers_formatted[['driver_id', 'driver_name']], on='driver_id')
        
        # Constructor champion
        team_season_pts = df_pts.groupby(['year', 'constructor_id'])['points'].sum().reset_index()
        idx_team_champs = team_season_pts.groupby('year')['points'].idxmax()
        team_champs = team_season_pts.loc[idx_team_champs].merge(self.constructors_formatted[['constructor_id', 'constructor_name']], on='constructor_id')
        
        merged = races_per_season.merge(driver_champs[['year', 'driver_name']], on='year', how='left')
        merged = merged.merge(team_champs[['year', 'constructor_name']], on='year', how='left')
        
        merged = merged.rename(columns={'driver_name': 'champion_driver', 'constructor_name': 'champion_constructor'})
        records = merged.sort_values(by='year', ascending=False).to_dict(orient='records')
        cleaned_records = [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in records]
        return cleaned_records
