# Data Preprocessing & Quality Report - RaceVision AI

This document contains a comprehensive audit of the raw motorsport datasets, detailing missing values, data inconsistencies, outliers, and the cleaning transformations applied to make the data model-ready.

## 1. Data Quality Analysis (Raw Datasets)

Below is the summary of the raw data properties before cleaning, identifying null values (including F1-specific `\N` placeholders) and duplicate rows:

| Table Name | Total Rows | Total Columns | Duplicate Rows | Null Columns (Count > 0) |
| :--- | :--- | :--- | :--- | :--- |
| `circuits` | 79 | 9 | 0 | alt (2.53%) |
| `constructors` | 211 | 5 | 0 | None |
| `drivers` | 854 | 9 | 0 | number (94.03%), code (88.64%) |
| `races` | 1,079 | 18 | 0 | time (67.75%), fp1_date (95.92%), fp1_time (97.96%)... |
| `results` | 25,420 | 18 | 0 | number (0.02%), position (42.45%), time (73.15%)... |
| `status` | 137 | 2 | 0 | None |
| `qualifying` | 9,155 | 9 | 0 | q1 (1.56%), q2 (47.0%), q3 (67.46%) |
| `lap_times` | 515,715 | 6 | 0 | None |
| `pit_stops` | 8,887 | 7 | 0 | None |
| `driver_standings` | 33,435 | 7 | 0 | None |
| `constructor_standings` | 12,721 | 7 | 0 | None |

## 2. Preprocessing & Cleaning Transformations

Each table was processed individually through a modular cleaning pipeline. The following transformations were successfully performed:

### Component: `circuits`
- Standardized column names to snake_case
- Replaced '\N' in 'alt' with NaN and cast to float
- Imputed missing altitude values with median (129.0m)
- Removed 0 duplicate circuits

### Component: `constructors`
- Standardized column names
- Removed 0 duplicate constructors

### Component: `drivers`
- Standardized column names
- Converted driver 'number' to nullable Int64
- Parsed 'dob' to datetime format
- Created composite 'driver_name' column
- Removed 0 duplicate drivers

### Component: `races`
- Standardized column names
- Fixed header mismatch (overrode 8-column header with correct 18 columns)
- Converted 'date' to datetime object
- Merged 'date' and 'time' into 'race_timestamp'
- Cleaned sub-sessions (fp1, fp2, fp3, quali, sprint) dates/times and consolidated them into timestamps
- Removed 0 duplicate races

### Component: `results`
- Standardized column names
- Replaced '\N' with NaN in results columns (position, milliseconds, fastest_lap, rank, fastest_lap_speed)
- Converted positions and lap counts to nullable Int64 types
- Converted fastest lap times (e.g. '1:24.320') to float seconds
- Identified 38 race results with abnormally long race times (>4 hours, likely red-flagged)
- Removed 0 duplicate race results

### Component: `status`
- Standardized column names
- Removed 0 duplicate status entries

### Component: `qualifying`
- Standardized column names
- Replaced '\N' in q1, q2, q3 columns with NaN
- Parsed qualifying string lap times (Q1/Q2/Q3) to float seconds
- Removed 0 duplicate qualifying records

### Component: `lap_times`
- Standardized column names
- Parsed lap time string into float seconds
- Identified 764 slow laps (>200s, likely safety car / red flag) and 0 fast laps (<45s, likely telemetry glitch/historic short layouts)
- Removed 0 duplicate lap time entries

### Component: `pit_stops`
- Standardized column names
- Converted duration to float seconds and synced with milliseconds
- Identified 285 pit stops >100s (representing car repairs or red flags)
- Removed 0 duplicate pit stop records

### Component: `standings`
- Standardized columns for both driver and constructor standings
- Converted points to float, and position & wins to integer types
- Removed 0 duplicate driver standings and 0 duplicate constructor standings

## 3. Detailed Data Profiling & Type Mapping

### Table: `circuits`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `circuitId` | `int64` | 79 | 0 | 0.0% |
| `circuitRef` | `object` | 79 | 0 | 0.0% |
| `name` | `object` | 79 | 0 | 0.0% |
| `location` | `object` | 76 | 0 | 0.0% |
| `country` | `object` | 36 | 0 | 0.0% |
| `lat` | `float64` | 78 | 0 | 0.0% |
| `lng` | `float64` | 78 | 0 | 0.0% |
| `alt` | `object` | 66 | 2 | 2.53% |
| `url` | `object` | 79 | 0 | 0.0% |

### Table: `constructors`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `constructorId` | `int64` | 211 | 0 | 0.0% |
| `constructorRef` | `object` | 211 | 0 | 0.0% |
| `name` | `object` | 211 | 0 | 0.0% |
| `nationality` | `object` | 24 | 0 | 0.0% |
| `url` | `object` | 174 | 0 | 0.0% |

### Table: `drivers`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `driverId` | `int64` | 854 | 0 | 0.0% |
| `driverRef` | `object` | 854 | 0 | 0.0% |
| `number` | `object` | 43 | 803 | 94.03% |
| `code` | `object` | 91 | 757 | 88.64% |
| `forename` | `object` | 474 | 0 | 0.0% |
| `surname` | `object` | 795 | 0 | 0.0% |
| `dob` | `object` | 836 | 0 | 0.0% |
| `nationality` | `object` | 42 | 0 | 0.0% |
| `url` | `object` | 854 | 0 | 0.0% |

### Table: `races`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `raceId` | `int64` | 1,079 | 0 | 0.0% |
| `year` | `int64` | 73 | 0 | 0.0% |
| `round` | `int64` | 22 | 0 | 0.0% |
| `circuitId` | `int64` | 77 | 0 | 0.0% |
| `name` | `object` | 53 | 0 | 0.0% |
| `date` | `object` | 1,079 | 0 | 0.0% |
| `time` | `object` | 33 | 731 | 67.75% |
| `url` | `object` | 1,079 | 0 | 0.0% |
| `fp1_date` | `object` | 44 | 1,035 | 95.92% |
| `fp1_time` | `object` | 11 | 1,057 | 97.96% |
| `fp2_date` | `object` | 44 | 1,035 | 95.92% |
| `fp2_time` | `object` | 11 | 1,057 | 97.96% |
| `fp3_date` | `object` | 38 | 1,041 | 96.48% |
| `fp3_time` | `object` | 8 | 1,060 | 98.24% |
| `quali_date` | `object` | 44 | 1,035 | 95.92% |
| `quali_time` | `object` | 9 | 1,057 | 97.96% |
| `sprint_date` | `object` | 6 | 1,073 | 99.44% |
| `sprint_time` | `object` | 2 | 1,076 | 99.72% |

### Table: `results`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `resultId` | `int64` | 25,420 | 0 | 0.0% |
| `raceId` | `int64` | 1,058 | 0 | 0.0% |
| `driverId` | `int64` | 854 | 0 | 0.0% |
| `constructorId` | `int64` | 210 | 0 | 0.0% |
| `number` | `object` | 129 | 6 | 0.02% |
| `grid` | `int64` | 35 | 0 | 0.0% |
| `position` | `object` | 33 | 10,790 | 42.45% |
| `positionText` | `object` | 39 | 0 | 0.0% |
| `positionOrder` | `int64` | 39 | 0 | 0.0% |
| `points` | `float64` | 39 | 0 | 0.0% |
| `laps` | `int64` | 172 | 0 | 0.0% |
| `time` | `object` | 6,586 | 18,594 | 73.15% |
| `milliseconds` | `object` | 6,788 | 18,595 | 73.15% |
| `fastestLap` | `object` | 79 | 18,447 | 72.57% |
| `rank` | `object` | 25 | 18,249 | 71.79% |
| `fastestLapTime` | `object` | 6,428 | 18,447 | 72.57% |
| `fastestLapSpeed` | `object` | 6,572 | 18,447 | 72.57% |
| `statusId` | `int64` | 135 | 0 | 0.0% |

### Table: `status`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `statusId` | `int64` | 137 | 0 | 0.0% |
| `status` | `object` | 137 | 0 | 0.0% |

### Table: `qualifying`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `qualifyId` | `int64` | 9,155 | 0 | 0.0% |
| `raceId` | `int64` | 427 | 0 | 0.0% |
| `driverId` | `int64` | 165 | 0 | 0.0% |
| `constructorId` | `int64` | 46 | 0 | 0.0% |
| `number` | `int64` | 53 | 0 | 0.0% |
| `position` | `int64` | 28 | 0 | 0.0% |
| `q1` | `object` | 8,078 | 143 | 1.56% |
| `q2` | `object` | 4,588 | 4,303 | 47.0% |
| `q3` | `object` | 2,879 | 6,176 | 67.46% |

### Table: `lap_times`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `raceId` | `int64` | 477 | 0 | 0.0% |
| `driverId` | `int64` | 136 | 0 | 0.0% |
| `lap` | `int64` | 87 | 0 | 0.0% |
| `position` | `int64` | 24 | 0 | 0.0% |
| `time` | `object` | 73,362 | 0 | 0.0% |
| `milliseconds` | `int64` | 73,362 | 0 | 0.0% |

### Table: `pit_stops`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `raceId` | `int64` | 218 | 0 | 0.0% |
| `driverId` | `int64` | 69 | 0 | 0.0% |
| `stop` | `int64` | 6 | 0 | 0.0% |
| `lap` | `int64` | 74 | 0 | 0.0% |
| `time` | `object` | 6,792 | 0 | 0.0% |
| `duration` | `object` | 6,336 | 0 | 0.0% |
| `milliseconds` | `int64` | 6,336 | 0 | 0.0% |

### Table: `driver_standings`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `driverStandingsId` | `int64` | 33,435 | 0 | 0.0% |
| `raceId` | `int64` | 1,058 | 0 | 0.0% |
| `driverId` | `int64` | 847 | 0 | 0.0% |
| `points` | `float64` | 402 | 0 | 0.0% |
| `position` | `int64` | 108 | 0 | 0.0% |
| `positionText` | `object` | 109 | 0 | 0.0% |
| `wins` | `int64` | 14 | 0 | 0.0% |

### Table: `constructor_standings`
| Column | Original Dtype | Unique Values | Null Count | Null % |
| :--- | :--- | :--- | :--- | :--- |
| `constructorStandingsId` | `int64` | 12,721 | 0 | 0.0% |
| `raceId` | `int64` | 994 | 0 | 0.0% |
| `constructorId` | `int64` | 159 | 0 | 0.0% |
| `points` | `float64` | 517 | 0 | 0.0% |
| `position` | `int64` | 22 | 0 | 0.0% |
| `positionText` | `object` | 23 | 0 | 0.0% |
| `wins` | `int64` | 20 | 0 | 0.0% |