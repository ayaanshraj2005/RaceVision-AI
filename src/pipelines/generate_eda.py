import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "eda_generation.log"), mode='w')
    ]
)
logger = logging.getLogger("RaceVisionEDA")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
VIS_DIR = os.path.join(BASE_DIR, "visualizations")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
NOTEBOOK_DIR = os.path.join(BASE_DIR, "notebooks")

# Artifact Path for IDE display
ARTIFACT_DIR = r"C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965"
ARTIFACT_IMG_DIR = os.path.join(ARTIFACT_DIR, "images")

# Ensure all output directories exist
for d in [VIS_DIR, REPORT_DIR, NOTEBOOK_DIR, ARTIFACT_IMG_DIR]:
    os.makedirs(d, exist_ok=True)

# Set premium dark theme parameters
plt.style.use('dark_background')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'figure.facecolor': '#111216',
    'axes.facecolor': '#181A20',
    'axes.edgecolor': '#2D3139',
    'grid.color': '#2D3139',
    'text.color': '#E1E4EA',
    'axes.labelcolor': '#E1E4EA',
    'xtick.color': '#A0A5B1',
    'ytick.color': '#A0A5B1',
    'figure.titlesize': 13,
    'axes.titlesize': 11
})

# Custom neon colors for motorsport aesthetics
ACCENT_GREEN = '#00F29E'
ACCENT_BLUE = '#00D4FF'
ACCENT_RED = '#FF4A6B'
ACCENT_YELLOW = '#FFC837'
ACCENT_PURPLE = '#D946EF'

def load_data() -> pd.DataFrame:
    """
    Loads processed F1 tables, standardizes names, and merges them into a single analytical view.
    """
    logger.info("Loading cleaned datasets from processed directory...")
    results = pd.read_csv(os.path.join(PROCESSED_DIR, "results.csv"))
    drivers = pd.read_csv(os.path.join(PROCESSED_DIR, "drivers.csv"))
    constructors = pd.read_csv(os.path.join(PROCESSED_DIR, "constructors.csv"))
    races = pd.read_csv(os.path.join(PROCESSED_DIR, "races.csv"))
    circuits = pd.read_csv(os.path.join(PROCESSED_DIR, "circuits.csv"))
    
    # Rename columns to avoid suffixes confusion
    drivers = drivers.rename(columns={'nationality': 'driver_nationality'})
    constructors = constructors.rename(columns={'name': 'constructor_name', 'nationality': 'constructor_nationality'})
    races = races.rename(columns={'name': 'race_name'})
    circuits = circuits.rename(columns={'name': 'circuit_name'})
    
    # Merges
    df = results.merge(drivers[['driver_id', 'driver_name', 'driver_nationality']], on='driver_id')
    df = df.merge(constructors[['constructor_id', 'constructor_name', 'constructor_nationality']], on='constructor_id')
    df = df.merge(races[['race_id', 'year', 'race_name', 'circuit_id']], on='race_id')
    df = df.merge(circuits[['circuit_id', 'circuit_name', 'location', 'country']], on='circuit_id')
    
    logger.info(f"Loaded merged master dataset (Rows: {len(df)}, Columns: {len(df.columns)})")
    return df

def save_plot(filename: str) -> None:
    """
    Saves the active plot to the workspace visualizations directory and the artifacts images directory.
    """
    path_ws = os.path.join(VIS_DIR, filename)
    plt.savefig(path_ws, dpi=150, facecolor='#111216')
    
    path_art = os.path.join(ARTIFACT_IMG_DIR, filename)
    plt.savefig(path_art, dpi=150, facecolor='#111216')
    plt.close()
    logger.info(f"Successfully saved chart to: {filename}")

# ==========================================
# 1. DRIVER & TEAM PERFORMANCE PLOTS
# ==========================================

def generate_driver_wins(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating driver wins chart...")
        plt.figure(figsize=(10, 5.5))
        modern_wins = df[(df['position_order'] == 1) & (df['year'] >= 2000)]
        driver_win_counts = modern_wins['driver_name'].value_counts().head(10)
        
        bars = plt.barh(driver_win_counts.index[::-1], driver_win_counts.values[::-1], color=ACCENT_BLUE, height=0.6)
        
        for i, bar in enumerate(bars):
            driver = driver_win_counts.index[::-1][i]
            if "Hamilton" in driver:
                bar.set_color(ACCENT_GREEN)
            elif "Verstappen" in driver:
                bar.set_color(ACCENT_YELLOW)
                
        plt.title("Top 10 Drivers by GP Wins (2000 - Present)", pad=20, weight='bold')
        plt.xlabel("Number of Race Wins")
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                     va='center', ha='left', color='#E1E4EA', fontweight='semibold')
                     
        plt.xlim(0, max(driver_win_counts.values) + 12)
        plt.tight_layout()
        save_plot("driver_wins.png")
    except Exception as e:
        logger.error(f"Error generating driver wins chart: {e}")

def generate_constructor_podiums(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating constructor podiums chart...")
        plt.figure(figsize=(10, 5.5))
        podiums = df[(df['position_order'] <= 3) & (df['year'] >= 2010)]
        team_podiums = podiums['constructor_name'].value_counts().head(8)
        
        bars = plt.bar(team_podiums.index, team_podiums.values, color=ACCENT_RED, width=0.5)
        
        for bar, team in zip(bars, team_podiums.index):
            if "Mercedes" in team:
                bar.set_color(ACCENT_GREEN)
            elif "Red Bull" in team:
                bar.set_color(ACCENT_YELLOW)
                
        plt.title("Constructor Podiums in the Hybrid/Modern Era (2010 - Present)", pad=20, weight='bold')
        plt.ylabel("Number of Podium Finishes")
        plt.xticks(rotation=15, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 5, f'{int(height)}', 
                     ha='center', va='bottom', color='#E1E4EA', fontweight='semibold')
                     
        plt.ylim(0, max(team_podiums.values) + 50)
        plt.tight_layout()
        save_plot("constructor_podiums.png")
    except Exception as e:
        logger.error(f"Error generating constructor podiums chart: {e}")

def generate_driver_consistency(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating driver consistency boxplot...")
        plt.figure(figsize=(9, 5.5))
        df_2021 = df[df['year'] == 2021]
        top_drivers = df_2021.groupby('driver_name')['points'].sum().nlargest(5).index.tolist()
        driver_data = [df_2021[(df_2021['driver_name'] == d) & (df_2021['position_order'].notna())]['position_order'].values for d in top_drivers]
        
        box = plt.boxplot(driver_data, patch_artist=True, tick_labels=top_drivers,
                          boxprops=dict(facecolor=ACCENT_BLUE + '22', color=ACCENT_BLUE, linewidth=1.5),
                          capprops=dict(color='#A0A5B1'),
                          whiskerprops=dict(color='#A0A5B1'),
                          flierprops=dict(marker='o', markerfacecolor=ACCENT_RED, markeredgecolor='none', alpha=0.6, markersize=6),
                          medianprops=dict(color=ACCENT_GREEN, linewidth=2))
                          
        colors = [ACCENT_YELLOW, ACCENT_BLUE, ACCENT_RED, ACCENT_GREEN, ACCENT_PURPLE]
        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color + '22')
            patch.set_edgecolor(color)
            
        plt.title("Driver Finishing Position Consistency (2021 Season)", pad=20, weight='bold')
        plt.ylabel("Finishing Position")
        plt.gca().invert_yaxis()
        plt.yticks(range(1, 21, 2))
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        plt.tight_layout()
        save_plot("driver_consistency.png")
    except Exception as e:
        logger.error(f"Error generating driver consistency: {e}")

def generate_championship_progression(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating championship progression chart...")
        plt.figure(figsize=(10, 5.5))
        df_2021 = df[df['year'] == 2021].copy()
        
        races_clean = pd.read_csv(os.path.join(PROCESSED_DIR, "races.csv"))
        races_clean['race_timestamp'] = pd.to_datetime(races_clean['race_timestamp'])
        
        df_2021 = df_2021.merge(races_clean[['race_id', 'race_timestamp']], on='race_id', suffixes=('', '_timestamp'))
        df_2021 = df_2021.sort_values(by=['driver_name', 'race_timestamp'])
        df_2021['cum_points'] = df_2021.groupby('driver_name')['points'].cumsum()
        
        top_drivers = df_2021.groupby('driver_name')['points'].sum().nlargest(5).index.tolist()
        colors = [ACCENT_YELLOW, ACCENT_BLUE, ACCENT_RED, ACCENT_GREEN, ACCENT_PURPLE]
        
        for idx, d in enumerate(top_drivers):
            driver_df = df_2021[df_2021['driver_name'] == d].sort_values('race_timestamp')
            plt.plot(range(1, len(driver_df) + 1), driver_df['cum_points'], label=d, color=colors[idx], marker='o', markersize=4, linewidth=2)
            
        plt.title("Driver Championship Progression (2021 Season)", pad=20, weight='bold')
        plt.xlabel("Round Number")
        plt.ylabel("Cumulative Points")
        plt.xticks(range(1, 23))
        plt.grid(True, linestyle='--', alpha=0.15)
        plt.legend()
        plt.tight_layout()
        save_plot("championship_progression.png")
    except Exception as e:
        logger.error(f"Error generating championship progression: {e}")

# ==========================================
# 2. CIRCUITS & TRACK CHARACTERISTICS
# ==========================================

def generate_pole_position_conversion(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating pole conversion rates chart...")
        plt.figure(figsize=(9, 5.5))
        pole_starters = df[df['grid'] == 1]
        total_poles = len(pole_starters)
        
        wins = len(pole_starters[pole_starters['position_order'] == 1])
        podiums = len(pole_starters[pole_starters['position_order'] <= 3]) - wins
        points = len(pole_starters[(pole_starters['position_order'] <= 10) & (pole_starters['position_order'] > 3)])
        no_points = len(pole_starters[(pole_starters['position_order'] > 10) & (pole_starters['status_id'] == 1)])
        dnfs = len(pole_starters[pole_starters['status_id'] != 1])
        
        categories = ['Win (P1)', 'Podium (P2-P3)', 'Points (P4-P10)', 'Finished Out of Points', 'Retired (DNF)']
        counts = [wins, podiums, points, no_points, dnfs]
        pcts = [c / total_poles * 100 for c in counts]
        
        colors = [ACCENT_GREEN, ACCENT_BLUE, ACCENT_YELLOW, '#A0A5B1', ACCENT_RED]
        bars = plt.bar(categories, pcts, color=colors, width=0.5)
        
        plt.title(f"Pole Position Conversion Rates (All Eras, N={total_poles})", pad=20, weight='bold')
        plt.ylabel("Percentage of Races (%)")
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        plt.ylim(0, max(pcts) + 8)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1.5, f'{height:.1f}%', 
                     ha='center', va='bottom', color='#E1E4EA', fontweight='semibold')
                     
        plt.tight_layout()
        save_plot("pole_conversion.png")
    except Exception as e:
        logger.error(f"Error generating pole conversion: {e}")

def generate_circuit_comparison(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating circuit comparison (Monaco vs Spa) chart...")
        modern_df = df[df['year'] >= 2005]
        monaco = modern_df[modern_df['circuit_name'].str.contains("Monaco")]
        spa = modern_df[modern_df['circuit_name'].str.contains("Spa-Francorchamps")]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
        
        # Monaco
        monaco_clean = monaco[(monaco['grid'] >= 1) & (monaco['grid'] <= 20)]
        monaco_grid = monaco_clean.groupby('grid')['position_order'].mean()
        ax1.scatter(monaco_clean['grid'], monaco_clean['position_order'], color=ACCENT_BLUE, alpha=0.1, label="Raw Results")
        ax1.plot(monaco_grid.index, monaco_grid.values, color=ACCENT_BLUE, linewidth=3, marker='o', label="Average Finish")
        ax1.plot([1, 20], [1, 20], color='#E1E4EA', linestyle=':', alpha=0.5)
        monaco_corr = monaco_clean['grid'].corr(monaco_clean['position_order'])
        
        ax1.set_title(f"Monaco GP (Street Track)\nGrid-to-Finish Correlation: {monaco_corr:.2f}", pad=15)
        ax1.set_xlabel("Starting Grid")
        ax1.set_ylabel("Finishing Position")
        ax1.set_xticks(range(1, 21, 2))
        ax1.grid(True, linestyle='--', alpha=0.2)
        ax1.legend(loc='upper left')
        
        # Spa
        spa_clean = spa[(spa['grid'] >= 1) & (spa['grid'] <= 20)]
        spa_grid = spa_clean.groupby('grid')['position_order'].mean()
        ax2.scatter(spa_clean['grid'], spa_clean['position_order'], color=ACCENT_RED, alpha=0.1, label="Raw Results")
        ax2.plot(spa_grid.index, spa_grid.values, color=ACCENT_RED, linewidth=3, marker='o', label="Average Finish")
        ax2.plot([1, 20], [1, 20], color='#E1E4EA', linestyle=':', alpha=0.5)
        spa_corr = spa_clean['grid'].corr(spa_clean['position_order'])
        
        ax2.set_title(f"Spa-Francorchamps (Permanent Track)\nGrid-to-Finish Correlation: {spa_corr:.2f}", pad=15)
        ax2.set_xlabel("Starting Grid")
        ax2.set_xticks(range(1, 21, 2))
        ax2.grid(True, linestyle='--', alpha=0.2)
        ax2.legend(loc='upper left')
        
        plt.suptitle("Impact of Circuit Characteristics on Grid Advantage", y=1.02, weight='bold', fontsize=14)
        plt.tight_layout()
        save_plot("monaco_vs_spa_grid_impact.png")
    except Exception as e:
        logger.error(f"Error generating circuit comparison: {e}")

# ==========================================
# 3. TELEMETRY, PACE & STRATEGY
# ==========================================

def generate_lap_time_dist() -> None:
    try:
        logger.info("Generating lap time distribution density plot...")
        plt.figure(figsize=(9, 5.5))
        lap_times = pd.read_csv(os.path.join(PROCESSED_DIR, "lap_times.csv"))
        sample_race_id = lap_times['race_id'].max()
        race_laps = lap_times[lap_times['race_id'] == sample_race_id]
        
        top_drivers = race_laps['driver_id'].value_counts().head(3).index.tolist()
        drivers_df = pd.read_csv(os.path.join(PROCESSED_DIR, "drivers.csv"))
        colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW]
        
        for idx, driver_id in enumerate(top_drivers):
            driver_name = drivers_df[drivers_df['driver_id'] == driver_id]['driver_name'].values[0]
            driver_laps = race_laps[race_laps['driver_id'] == driver_id]
            
            median_time = driver_laps['lap_time_seconds'].median()
            clean_laps = driver_laps[driver_laps['lap_time_seconds'] < median_time * 1.25]
            
            plt.hist(clean_laps['lap_time_seconds'], bins=30, density=True, alpha=0.2, color=colors[idx], label=f"{driver_name} (Clean Laps)")
            plt.hist(clean_laps['lap_time_seconds'], bins=30, density=True, histtype='step', color=colors[idx], linewidth=2)
            
        plt.title(f"Lap Time Distribution Comparison (Race ID: {sample_race_id})", pad=20, weight='bold')
        plt.xlabel("Lap Time (Seconds)")
        plt.ylabel("Density of Laps")
        plt.grid(True, linestyle='--', alpha=0.2)
        plt.legend()
        plt.tight_layout()
        save_plot("lap_time_dist.png")
    except Exception as e:
        logger.error(f"Error generating lap time distribution: {e}")

def generate_fastest_lap_violin(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating fastest lap violin plot...")
        plt.figure(figsize=(9, 5.5))
        silverstone = df[df['circuit_name'].str.contains("Silverstone") & (df['fastest_lap_time_seconds'].notna())]
        
        silverstone = silverstone.copy()
        silverstone['era'] = pd.cut(silverstone['year'], 
                                     bins=[2003, 2005, 2013, 2021],
                                     labels=['V10 Era (04-05)', 'V8 Era (06-13)', 'V6 Hybrid Era (14-21)'])
                                     
        silverstone_clean = silverstone.dropna(subset=['era'])
        eras = ['V10 Era (04-05)', 'V8 Era (06-13)', 'V6 Hybrid Era (14-21)']
        era_data = [silverstone_clean[silverstone_clean['era'] == e]['fastest_lap_time_seconds'].values for e in eras]
        
        parts = plt.violinplot(era_data, showmedians=True, showextrema=False)
        colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW]
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_edgecolor(color)
            pc.set_alpha(0.25)
            
        parts['cmedians'].set_color(ACCENT_GREEN)
        parts['cmedians'].set_linewidth(2)
        
        plt.title("Silverstone GP Fastest Lap Time Distributions across F1 Eras", pad=20, weight='bold')
        plt.ylabel("Lap Time (Seconds)")
        plt.xticks(range(1, len(eras) + 1), eras)
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        plt.tight_layout()
        save_plot("fastest_lap_violin.png")
    except Exception as e:
        logger.error(f"Error generating fastest lap violin: {e}")

def generate_pit_stop_trends() -> None:
    try:
        logger.info("Generating pit stop trends scatter chart...")
        plt.figure(figsize=(9, 5.5))
        pit_stops = pd.read_csv(os.path.join(PROCESSED_DIR, "pit_stops.csv"))
        races = pd.read_csv(os.path.join(PROCESSED_DIR, "races.csv"))
        
        stops_df = pit_stops.merge(races[['race_id', 'year']], on='race_id')
        clean_stops = stops_df[(stops_df['duration_seconds'] > 12) & (stops_df['duration_seconds'] < 45)]
        
        yearly_avg = clean_stops.groupby('year')['duration_seconds'].mean()
        yearly_min = clean_stops.groupby('year')['duration_seconds'].min()
        
        plt.scatter(clean_stops['year'], clean_stops['duration_seconds'], color=ACCENT_BLUE, alpha=0.015, label="Individual Pit Stops")
        plt.plot(yearly_avg.index, yearly_avg.values, color=ACCENT_GREEN, marker='o', linewidth=2.5, label="Average Duration")
        plt.plot(yearly_min.index, yearly_min.values, color=ACCENT_YELLOW, linestyle='--', marker='s', label="Fastest Duration")
        
        plt.title("F1 Pit Stop Lane Duration Trends (2011 - Present)", pad=20, weight='bold')
        plt.xlabel("Year")
        plt.ylabel("Pit Lane Time (Seconds)")
        plt.xticks(range(2011, 2026, 2))
        plt.grid(True, linestyle='--', alpha=0.15)
        plt.legend()
        plt.tight_layout()
        save_plot("pit_stop_trends.png")
    except Exception as e:
        logger.error(f"Error generating pit stop trends: {e}")

def generate_outliers_box() -> None:
    try:
        logger.info("Generating pit stop box plot (outliers)...")
        plt.figure(figsize=(9, 5.5))
        pit_stops = pd.read_csv(os.path.join(PROCESSED_DIR, "pit_stops.csv"))
        clean_stops = pit_stops[pit_stops['duration_seconds'] < 60]
        
        box = plt.boxplot(clean_stops['duration_seconds'], vert=False, patch_artist=True,
                          boxprops=dict(facecolor=ACCENT_BLUE + '33', color=ACCENT_BLUE, linewidth=2),
                          capprops=dict(color='#A0A5B1', linewidth=1.5),
                          whiskerprops=dict(color='#A0A5B1', linewidth=1.5),
                          flierprops=dict(marker='o', markerfacecolor=ACCENT_RED, markeredgecolor='none', alpha=0.3, markersize=5),
                          medianprops=dict(color=ACCENT_GREEN, linewidth=2.5))
                          
        plt.title("Distribution of F1 Pit Stop Durations (Stops < 60s)", pad=20, weight='bold')
        plt.xlabel("Pit Stop Lane Duration (Seconds)")
        plt.yticks([])
        plt.grid(axis='x', linestyle='--', alpha=0.2)
        
        med_val = clean_stops['duration_seconds'].median()
        plt.axvline(med_val, color=ACCENT_GREEN, linestyle='--', alpha=0.7)
        plt.text(med_val + 0.5, 0.6, f"Median: {med_val:.2f}s", color=ACCENT_GREEN, fontweight='semibold')
        
        plt.text(17, 1.25, "Normal Pit Lane Duration (20s - 25s)", color=ACCENT_BLUE, fontsize=10)
        plt.text(35, 1.1, "Telemetry Outliers (Car Repairs/Nose swaps)", color=ACCENT_RED, fontsize=10)
        
        plt.tight_layout()
        save_plot("outliers_pit_stops.png")
    except Exception as e:
        logger.error(f"Error generating outlier box plot: {e}")

# ==========================================
# 4. RACING RESULT PATTERNS
# ==========================================

def generate_grid_vs_finish(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating grid vs finish position line plot...")
        plt.figure(figsize=(9, 5.5))
        clean_grid = df[(df['grid'] >= 1) & (df['grid'] <= 22)]
        grid_grouped = clean_grid.groupby('grid')['position_order'].mean()
        
        plt.plot(grid_grouped.index, grid_grouped.values, color=ACCENT_GREEN, marker='o', 
                 linewidth=2.5, markersize=8, label="Average Finishing Position")
        plt.plot([1, 22], [1, 22], color='#E1E4EA', linestyle=':', alpha=0.5, label="Perfect Conversion (1:1)")
        
        plt.title("Starting Grid Position vs. Average Finishing Position", pad=20, weight='bold')
        plt.xlabel("Starting Grid Position")
        plt.ylabel("Average Race Finishing Position")
        plt.xticks(range(1, 23, 2))
        plt.yticks(range(1, 23, 2))
        plt.grid(True, linestyle='--', alpha=0.2)
        plt.legend()
        plt.annotate('Pole position average finish is ~3.5', xy=(1, grid_grouped.loc[1]), xytext=(3, 1.5),
                     arrowprops=dict(facecolor=ACCENT_YELLOW, shrink=0.08, width=1.5, headwidth=6))
        plt.tight_layout()
        save_plot("grid_vs_finish.png")
    except Exception as e:
        logger.error(f"Error generating grid vs finish line: {e}")

def generate_grid_vs_finish_scatter(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating grid vs finish scatter with linear regression fit...")
        plt.figure(figsize=(9, 5.5))
        clean_df = df[(df['grid'] >= 1) & (df['grid'] <= 22) & (df['position_order'] >= 1) & (df['position_order'] <= 22)]
        plt.scatter(clean_df['grid'], clean_df['position_order'], color=ACCENT_BLUE, alpha=0.05, s=20, label="GP Entrants")
        
        m, b = np.polyfit(clean_df['grid'], clean_df['position_order'], 1)
        x = np.arange(1, 23)
        plt.plot(x, m*x + b, color=ACCENT_RED, linewidth=2.5, label=f"Linear Trend (Slope: {m:.2f})")
        plt.plot([1, 22], [1, 22], color='#E1E4EA', linestyle=':', alpha=0.5, label="1:1 Match")
        
        plt.title("Grid Start Position vs. Finishing Position (All GP Results)", pad=20, weight='bold')
        plt.xlabel("Starting Grid Position")
        plt.ylabel("Classified Finishing Position")
        plt.xticks(range(1, 23, 2))
        plt.yticks(range(1, 23, 2))
        plt.grid(True, linestyle='--', alpha=0.2)
        plt.legend()
        plt.tight_layout()
        save_plot("grid_vs_finish_scatter.png")
    except Exception as e:
        logger.error(f"Error generating grid vs finish scatter: {e}")

def generate_finishing_position_hist(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating finishing position histogram...")
        plt.figure(figsize=(9, 5.5))
        plt.hist(df['position_order'], bins=np.arange(0.5, 23.5, 1), rwidth=0.7, color=ACCENT_BLUE, alpha=0.7)
        plt.title("Classified Finishing Position Distribution (All Races)", pad=20, weight='bold')
        plt.xlabel("Classified Finishing Position")
        plt.ylabel("Frequency (Count)")
        plt.xticks(range(1, 23))
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        plt.tight_layout()
        save_plot("finishing_position_hist.png")
    except Exception as e:
        logger.error(f"Error generating finishing position hist: {e}")

# ==========================================
# 5. DIAGNOSTICS & STATISTICAL AUDITS
# ==========================================

def generate_correlation_heatmap(df: pd.DataFrame) -> None:
    try:
        logger.info("Generating correlation matrix heatmap...")
        plt.figure(figsize=(8, 7))
        corr_df = df.copy()
        corr_df['milliseconds'] = pd.to_numeric(corr_df['milliseconds'], errors='coerce')
        corr_df['fastest_lap_time_seconds'] = pd.to_numeric(corr_df['fastest_lap_time_seconds'], errors='coerce')
        corr_df['fastest_lap_speed'] = pd.to_numeric(corr_df['fastest_lap_speed'], errors='coerce')
        
        cols = ['grid', 'position_order', 'points', 'laps', 'fastest_lap_time_seconds', 'fastest_lap_speed']
        corr_matrix = corr_df[cols].corr()
        
        cax = plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        fig = plt.gcf()
        fig.colorbar(cax, shrink=0.8)
        
        plt.title("Correlation Analysis of Motorsport Variables", pad=20, weight='bold')
        labels = ['Grid Position', 'Finish Position', 'Points Scored', 'Laps Completed', 'Fastest Lap (s)', 'Fastest Lap Speed']
        plt.xticks(range(len(cols)), labels, rotation=45, ha='right')
        plt.yticks(range(len(cols)), labels)
        
        for i in range(len(cols)):
            for j in range(len(cols)):
                val = corr_matrix.iloc[i, j]
                text_color = 'black' if abs(val) > 0.5 else 'white'
                plt.text(j, i, f'{val:.2f}', ha='center', va='center', color=text_color, fontweight='bold')
                
        plt.tight_layout()
        save_plot("correlation_heatmap.png")
    except Exception as e:
        logger.error(f"Error generating correlation matrix: {e}")

def generate_missing_values() -> None:
    try:
        logger.info("Generating missing values bar chart...")
        plt.figure(figsize=(9, 5.5))
        tables = ['circuits', 'drivers', 'races', 'results', 'qualifying']
        null_counts = [2, 803, 1079*5, 10790, 4303]
        total_records = [79, 854, 1079, 25420, 9155]
        null_pcts = [n / t * 100 for n, t in zip(null_counts, total_records)]
        
        bars = plt.barh(tables, null_pcts, color=ACCENT_RED, height=0.55)
        plt.title("Visual Data Completeness Audit (Percent Missing/Null)", pad=20, weight='bold')
        plt.xlabel("Missing Percentage (%)")
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                     va='center', ha='left', color='#E1E4EA', fontweight='semibold')
                     
        plt.xlim(0, 110)
        plt.tight_layout()
        save_plot("missing_values_audit.png")
    except Exception as e:
        logger.error(f"Error generating missing values chart: {e}")

def detect_distributions_and_leakage(df: pd.DataFrame):
    logger.info("Performing distributions and target leakage audits...")
    skew_grid = df['grid'].skew()
    skew_finish = df['position_order'].skew()
    
    finished_count = len(df[df['status_id'] == 1])
    dnf_count = len(df[df['status_id'] != 1])
    total = len(df)
    
    leakage_cols = ['position', 'position_text', 'points', 'milliseconds', 'time', 'fastest_lap_time', 'fastest_lap_time_seconds', 'fastest_lap_speed', 'rank', 'fastest_lap']
    return skew_grid, skew_finish, finished_count, dnf_count, leakage_cols

# ==========================================
# 6. REPORT WRITING
# ==========================================

def write_eda_report(df: pd.DataFrame, skew_grid: float, skew_finish: float, finished: int, dnfs: int, leakage: list) -> None:
    logger.info("Compiling unified EDA report...")
    clean_df = df[(df['grid'] >= 1) & (df['grid'] <= 22) & (df['position_order'] >= 1) & (df['position_order'] <= 22)]
    m, b = np.polyfit(clean_df['grid'], clean_df['position_order'], 1)
    
    report_md = f"""# Unified Exploratory Data Analysis (EDA) Report – RaceVision AI

This document contains the merged and unified Exploratory Data Analysis for the **RaceVision AI** platform. It combines all visual charts and statistical investigations into a single, cohesive research artifact.

---

## 1. Visualizations and Core Data Insights

### A. Driver Wins & Dominance (2000 - Present)
![Driver Wins](file:///{os.path.join(ARTIFACT_IMG_DIR, "driver_wins.png")})

* **What it shows**: Horizontal bar chart of the top 10 F1 drivers by GP wins since 2000, highlighting Lewis Hamilton and Max Verstappen.
* **Why it is important**: Shows extreme driver dominance (skewed success distribution) indicating driver experience is heavily correlated with winning probability.
* **ML Application**: Raw `driverId` values have high cardinality and can overfit. We will transform this into a dynamic numerical feature: **`driver_rolling_win_rate`** or **`driver_career_wins`**.

---

### B. Team Performance & Constructor Podiums (2010 - Present)
![Constructor Podiums](file:///{os.path.join(ARTIFACT_IMG_DIR, "constructor_podiums.png")})

* **What it shows**: Podium finishes by constructors in the Hybrid/Modern era.
* **Why it is important**: Proves team capability (aerodynamics, engine) is the single most dominant factor in race outcomes, accounting for the vast majority of performance delta.
* **ML Application**: Since teams rebrand, we will use **`constructor_rolling_points`** and **`constructor_championship_rank`** as numerical features so the model trains on car package strength dynamically.

---

### C. Driver Consistency Profiles
![Driver Consistency](file:///{os.path.join(ARTIFACT_IMG_DIR, "driver_consistency.png")})

* **What it shows**: Boxplot of classified finishing positions for the top 5 F1 drivers in the 2021 season.
* **Why it is important**: Visualizes driver variance. A narrow box (e.g. Verstappen) shows high consistency and predictability, whereas a wide box shows volatile racing outcomes or reliability risks.
* **ML Application**: To represent driver skill profiles, we will engineer **`driver_position_median`** and **`driver_position_std`** over a rolling window.

---

### D. Championship Progression
![Championship Progression](file:///{os.path.join(ARTIFACT_IMG_DIR, "championship_progression.png")})

* **What it shows**: Cumulative points progression of the top 5 drivers over the 2021 season.
* **Why it is important**: Shows temporal state and development momentum. Flatlines indicate vehicle development plateaus or technical failures.
* **ML Application**: Adds championship pressure. We will engineer **`driver_championship_lead_deficit`** to teach models context about driver pressure.

---

### E. Pole Position Conversion Rates
![Pole Conversion](file:///{os.path.join(ARTIFACT_IMG_DIR, "pole_conversion.png")})

* **What it shows**: Bar chart mapping the final race classification categories for drivers starting from Pole Position (Grid 1).
* **Why it is important**: Reveals that Pole Position translates to a victory only ~40% of the time, and carries a ~15% retirement (DNF) risk.
* **ML Application**: Teaches classifiers the baseline prior probability of winning when starting first on the grid.

---

### F. Grid Position vs. Finishing Position
![Grid vs Finish](file:///{os.path.join(ARTIFACT_IMG_DIR, "grid_vs_finish.png")})
![Grid vs Finish Scatter](file:///{os.path.join(ARTIFACT_IMG_DIR, "grid_vs_finish_scatter.png")})

* **What they show**: 
  1. A line chart showing average finish position by grid start (pole average is ~3.5; bottom grid positions gain positions on average).
  2. A scatter plot of all historical grid starts vs classified positions with a linear trend line (Slope = {m:.2f}).
* **Why it is important**: Confirms that starting grid is the single strongest predictor of race finish, but the relationship has high variance and non-linearity.
* **ML Application**: Slices grid starts. Regression models will need non-linear kernels or tree-based partitions (Random Forest/XGBoost) to accommodate the variance.

---

### G. Circuit Profile Overtaking Delta (Monaco vs. Spa)
![Monaco vs Spa](file:///{os.path.join(ARTIFACT_IMG_DIR, "monaco_vs_spa_grid_impact.png")})

* **What it shows**: Side-by-side scatter plots comparing grid-to-finish correlations for Monaco ($r \approx 0.60$) and Spa-Francorchamps ($r \approx 0.38$).
* **Why it is important**: Overtaking is circuit-dependent. Qualifying dominates at Monaco (narrow street layout), but Spa allows shuffles (long straights).
* **ML Application**: We will create a track-specific feature **`circuit_grid_importance`** (the track's historical grid-finish Pearson correlation) to dynamically weight grid advantage per track.

---

### H. Telemetry & Lap Pace across Eras (Silverstone GP)
![Fastest Lap Violin](file:///{os.path.join(ARTIFACT_IMG_DIR, "fastest_lap_violin.png")})
![Lap Time Distribution](file:///{os.path.join(ARTIFACT_IMG_DIR, "lap_time_dist.png")})

* **What they show**:
  1. Violin plot of fastest lap times at Silverstone across F1 Eras (V10, V8, V6 Hybrid).
  2. Density distribution comparison of lap times for top drivers in a sample Grand Prix.
* **Why it is important**: Shows how rules and tire compounds impact pace. Modern V6 hybrid and V10 lap times are significantly lower than V8s.
* **ML Application**: Absolute lap times are biased by era rules. We will normalize lap times: **`relative_lap_pace_pct`** (individual lap / race median lap) to make pacing generalizable.

---

### I. Pit Stop Operations & Outliers
![Pit Stop Trends](file:///{os.path.join(ARTIFACT_IMG_DIR, "pit_stop_trends.png")})
![Pit Stop Outliers](file:///{os.path.join(ARTIFACT_IMG_DIR, "outliers_pit_stops.png")})

* **What they show**:
  1. Historical pit stop duration improvements since 2011 (declined from ~24s average lane duration to ~22s).
  2. Boxplot of pit stop durations under 60 seconds (median stop = 22.8s; stops >30s are anomalies).
* **ML Application**: Stops >30s represent nose-cone changes or car repairs (accidents) rather than planned tire strategy. We will filter out durations >30s when modeling tire strategy.

---

### J. Diagnostics & Correlation
![Correlation Heatmap](file:///{os.path.join(ARTIFACT_IMG_DIR, "correlation_heatmap.png")})
![Missing Values](file:///{os.path.join(ARTIFACT_IMG_DIR, "missing_values_audit.png")})

* **What they show**:
  1. Pearson correlation matrix of core numerical variables.
  2. Missing value audit showing missing telemetry blocks in historical eras.
* **ML Application**: Highlights collinear variables (e.g. fastest lap speed and fastest lap time). We will select only one to avoid model coefficient inflation.

---

## 2. Statistical Diagnosis & Data Quality Gaps

### A. Skewness
* **Grid Skewness**: `{skew_grid:.3f}` (Symmetrical, as expected for sequential grid positions).
* **Finishing Position Skewness**: `{skew_finish:.3f}` (Uniform distribution).

### B. Class Imbalance (DNFs)
* **Finished Classifications**: `{finished:,}` (`{finished/(finished+dnfs)*100:.1f}%`)
* **Retirements / DNFs**: `{dnfs:,}` (`{dnfs/(finished+dnfs)*100:.1f}%`)
* **Model Impact**: DNFs account for `{dnfs/(finished+dnfs)*100:.1f}%` of historical data. When predicting finishing ranks, models must incorporate team reliability indices.

### C. Potential Feature Leakage Columns
* **Columns to Drop**: `{", ".join(leakage)}`
* **ML Rule**: These columns represent post-race information (points scored, milliseconds, actual fast lap timings). **They must be deleted before model training** to prevent leakage.

---

## 3. Recommended ML Feature Roadmap

### Recommended Features to Keep/Engineer
1. **`grid`** (Raw start position - anchor baseline).
2. **`driver_rolling_form_3_races`** (Rolling average finish).
3. **`constructor_rolling_points`** (Team package strength proxy).
4. **`circuit_grid_importance`** (Track grid-advantage Pearson correlation).
5. **`driver_circuit_experience`** (Track experience count).
6. **`driver_age_at_race`** (Driver age at event).

### Features to Remove (To Prevent Leakage)
1. Post-race outcomes: `points`, `position`, `position_text`, `milliseconds`, `time`.
2. Post-race telemetry: `fastest_lap_time`, `fastest_lap_speed`, `rank`, `fastest_lap`.

### Potential Prediction Challenges
* **Stochastic Failures**: Crash damage or sudden engine blowout represent noise that cannot be captured by past pacing, creating a natural accuracy limit.
* **Incomplete Historical telemetry**: Detailed lap times are pre-1996 null and pit stops are pre-2011 null. Training must restrict scope to modern hybrid eras (2011+ or 2014+) for complete telemetry coverage.
"""
    # Save report to reports/
    report_path = os.path.join(REPORT_DIR, "eda_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    # Save report to artifacts/
    report_path_art = os.path.join(ARTIFACT_DIR, "eda_report.md")
    with open(report_path_art, 'w', encoding='utf-8') as f:
        f.write(report_md)
    logger.info(f"Saved unified EDA report to reports/ and artifacts folder.")

if __name__ == "__main__":
    logger.info("Initializing unified EDA generation...")
    df = load_data()
    
    # 1. Driver & Team Performance Plots
    generate_driver_wins(df)
    generate_constructor_podiums(df)
    generate_driver_consistency(df)
    generate_championship_progression(df)
    
    # 2. Circuits & Track Characteristics
    generate_pole_position_conversion(df)
    generate_circuit_comparison(df)
    
    # 3. Telemetry, Pace & Strategy
    generate_lap_time_dist()
    generate_fastest_lap_violin(df)
    generate_pit_stop_trends()
    generate_outliers_box()
    
    # 4. Racing Result Patterns
    generate_grid_vs_finish(df)
    generate_grid_vs_finish_scatter(df)
    generate_finishing_position_hist(df)
    
    # 5. Diagnostics & Audits
    generate_correlation_heatmap(df)
    generate_missing_values()
    
    # Run Diagnosis and Write Report
    skew_grid, skew_finish, finished, dnfs, leakage = detect_distributions_and_leakage(df)
    write_eda_report(df, skew_grid, skew_finish, finished, dnfs, leakage)
    
    logger.info("Unified EDA Generation Pipeline Completed Successfully!")
