import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from src.config.settings import MODELS_DIR, PROCESSED_DIR
from sklearn.linear_model import LinearRegression, LogisticRegression
from src.services.database_service import DatabaseService
import logging

logger = logging.getLogger("RaceVisionPredictionService")

class PredictionService:
    def __init__(self):
        self.scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        self.reg_model_path = os.path.join(MODELS_DIR, "best_regressor.joblib")
        self.clf_model_path = os.path.join(MODELS_DIR, "best_classifier.joblib")
        
        # Verify model files exist
        if not os.path.exists(self.scaler_path) or not os.path.exists(self.reg_model_path) or not os.path.exists(self.clf_model_path):
            raise FileNotFoundError("Trained models not found. Please run Phase 5 training pipeline first.")
            
        self.scaler = joblib.load(self.scaler_path)
        self.reg_model = joblib.load(self.reg_model_path)
        self.clf_model = joblib.load(self.clf_model_path)
        self.db = DatabaseService()
        
        # Load unique driver and team pairings for validation
        self.valid_pairings = set()
        self.valid_season_pairings = {}
        self.valid_drivers = {}
        self.valid_constructors = {}
        ml_ready_path = os.path.join(PROCESSED_DIR, "ml_ready_dataset.csv")
        if os.path.exists(ml_ready_path):
            try:
                df_ml = pd.read_csv(ml_ready_path)
                for _, row in df_ml.iterrows():
                    d_name = str(row['driver_name']).strip()
                    c_name = str(row['constructor_name']).strip()
                    year = int(row['year'])
                    self.valid_pairings.add((d_name.lower(), c_name.lower()))
                    self.valid_drivers[d_name.lower()] = d_name
                    self.valid_constructors[c_name.lower()] = c_name
                    
                    if year not in self.valid_season_pairings:
                        self.valid_season_pairings[year] = set()
                    self.valid_season_pairings[year].add((d_name.lower(), c_name.lower()))
            except Exception:
                pass

        self.features = [
            'grid', 'driver_age', 'driver_experience', 'driver_recent_form', 
            'driver_rolling_grid', 'driver_avg_finish', 'driver_consistency', 
            'driver_win_rate', 'driver_podium_rate', 'driver_top10_rate', 
            'driver_dnf_rate', 'grid_delta_to_avg', 'constructor_strength_index', 
            'circuit_familiarity', 'circuit_grid_importance', 'is_home_race'
        ]

    def validate_driver_constructor(self, driver_name: str, constructor_name: str) -> Tuple[bool, str]:
        return self.validate_driver_constructor_season(driver_name, constructor_name, None)

    def validate_driver_constructor_season(self, driver_name: str, constructor_name: str, season: Optional[int] = None) -> Tuple[bool, str]:
        d_lower = driver_name.lower().strip()
        c_lower = constructor_name.lower().strip()
        
        # If dataset wasn't loaded, skip validation to prevent hard locks
        if not self.valid_drivers:
            return True, ""
            
        if d_lower not in self.valid_drivers:
            return False, f"Driver '{driver_name}' is not recognized in our database."
            
        if c_lower not in self.valid_constructors:
            return False, f"Constructor/Team '{constructor_name}' is not recognized in our database."
            
        if season is not None and season in self.valid_season_pairings:
            pairings = self.valid_season_pairings[season]
            if (d_lower, c_lower) not in pairings:
                # Find matching constructors for this driver in this season
                matching_teams = [
                    self.valid_constructors[c] for d, c in pairings if d == d_lower
                ]
                teams_str = ", ".join(matching_teams) if matching_teams else "None"
                return False, f"Driver '{driver_name}' did not drive for team '{constructor_name}' in the {season} season. Valid team(s) for this driver in {season}: {teams_str}."
        else:
            if (d_lower, c_lower) not in self.valid_pairings:
                # Find matching constructors for this driver
                matching_teams = [
                    self.valid_constructors[c] for d, c in self.valid_pairings if d == d_lower
                ]
                teams_str = ", ".join(matching_teams) if matching_teams else "None"
                return False, f"Driver '{driver_name}' has no record of driving for team '{constructor_name}'. Valid team(s) for this driver: {teams_str}."
            
        return True, ""

    def get_drivers_list(self, season: Optional[int] = None) -> List[str]:
        ml_ready_path = os.path.join(PROCESSED_DIR, "ml_ready_dataset.csv")
        if not os.path.exists(ml_ready_path):
            return sorted(list(self.valid_drivers.values()))
        try:
            df_ml = pd.read_csv(ml_ready_path)
            if season is not None:
                df_ml = df_ml[df_ml['year'] == season]
            return sorted(df_ml['driver_name'].unique().tolist())
        except Exception:
            return sorted(list(self.valid_drivers.values()))

    def get_driver_details(self, driver_name: str, season: Optional[int] = None) -> Optional[Dict[str, Any]]:
        d_lower = driver_name.lower().strip()
        ml_ready_path = os.path.join(PROCESSED_DIR, "ml_ready_dataset.csv")
        if not os.path.exists(ml_ready_path):
            return None
        
        try:
            df_ml = pd.read_csv(ml_ready_path)
            # Filter by driver name
            df_driver = df_ml[df_ml['driver_name'].str.lower().str.strip() == d_lower]
            if df_driver.empty:
                return None
            
            # Filter by season
            if season is not None:
                df_season = df_driver[df_driver['year'] == season]
                if df_season.empty:
                    # Fallback to the latest season available for this driver
                    season = int(df_driver['year'].max())
                    df_season = df_driver[df_driver['year'] == season]
            else:
                season = int(df_driver['year'].max())
                df_season = df_driver[df_driver['year'] == season]
                
            if df_season.empty:
                return None
                
            # Sort chronologically by race_id or round to get the latest race row in that season
            df_season = df_season.sort_values(by='race_id')
            row = df_season.iloc[-1]
            
            # Return matching structure
            return {
                "driver": str(row['driver_name']),
                "team": str(row['constructor_name']),
                "recent_form": float(row['driver_recent_form']),
                "team_strength": float(row['constructor_strength_index']),
                "experience": int(row['driver_experience']),
                "constructor_strength": float(row['constructor_strength_index']),
                "historical_win_rate": float(row['driver_win_rate']),
                "age": float(row['driver_age']),
                "rolling_grid": float(row['driver_rolling_grid']),
                "avg_finish": float(row['driver_avg_finish']),
                "consistency": float(row['driver_consistency']),
                "podium_rate": float(row['driver_podium_rate']),
                "top10_rate": float(row['driver_top10_rate']),
                "dnf_rate": float(row['driver_dnf_rate']),
                "grid_delta_to_avg": float(row['grid_delta_to_avg']),
                "season": int(row['year'])
            }
        except Exception as e:
            logger.error(f"Error in get_driver_details: {str(e)}")
            return None


    def _prepare_data(self, entries: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Helper to convert entries list to DataFrame and scale using loaded scaler.
        """
        df = pd.DataFrame(entries)
        X_scaled = self.scaler.transform(df[self.features])
        return df, X_scaled

    def _validate_and_adjust_raw_scores(self, df: pd.DataFrame, preds: np.ndarray) -> np.ndarray:
        """
        Production-grade validation engine. Soft-clips model prediction scores
        using motorsport domain physics and constraints (e.g. driver form, team capabilities, grid bounds).
        """
        adjusted_preds = []
        for idx, row in df.iterrows():
            grid = float(row['grid'])
            recent_form = float(row['driver_recent_form'])
            team_strength = float(row['constructor_strength_index'])
            pred_score = float(preds[idx])

            # Normalize driver and team capabilities
            # driver form factor (0 to 1, where 1 is best form)
            ff = np.clip(1.0 - (recent_form - 1.0) / 19.0, 0.0, 1.0)
            # team strength factor (0 to 1, where 1 is best team)
            csf = np.clip(team_strength / 50.0, 0.0, 1.0)
            # Combined performance index
            cpf = 0.6 * csf + 0.4 * ff

            # Physical racing bounds: How many positions can a driver realistically gain/lose?
            # E.g. starting P15 in a slow car cannot predict P1.
            max_gained = 3.0 + 12.0 * cpf # Up to 15 spots for elite packages, 3 spots for rookies/slow cars
            max_lost = 4.0 + 14.0 * (1.0 - cpf) # Up to 18 spots lost for bad packages, 4 spots for elite packages

            min_realistic_pos = np.clip(grid - max_gained, 1.0, 24.0)
            max_realistic_pos = np.clip(grid + max_lost, 1.0, 24.0)

            # Soft clip predicted raw position score within realistic boundaries
            adjusted_score = np.clip(pred_score, min_realistic_pos, max_realistic_pos)
            adjusted_preds.append(adjusted_score)

        return np.array(adjusted_preds)

    def predict_finish_position(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df, X_scaled = self._prepare_data(entries)
        
        # Support linear models drop if LinearRegression is best_regressor
        if isinstance(self.reg_model, LinearRegression):
            lr_features = [col for col in self.features if col not in ['grid_delta_to_avg', 'driver_avg_finish']]
            X_df = pd.DataFrame(X_scaled, columns=self.features)
            preds = self.reg_model.predict(X_df[lr_features])
        else:
            preds = self.reg_model.predict(X_scaled)
            
        # Validate and adjust predictions
        preds = self._validate_and_adjust_raw_scores(df, preds)
        
        df['predicted_raw_score'] = preds
        df['predicted_finishing_position'] = df['predicted_raw_score'].rank(method='first').astype(int)
        
        return df[['driver_id', 'driver_name', 'predicted_raw_score', 'predicted_finishing_position']].to_dict(orient='records')

    def predict_podium_probability(self, entries: List[Dict[str, Any]], predicted_positions: List[int] = None) -> List[Dict[str, Any]]:
        df, X_scaled = self._prepare_data(entries)
        
        if isinstance(self.clf_model, LogisticRegression):
            lr_features = [col for col in self.features if col not in ['grid_delta_to_avg', 'driver_avg_finish']]
            X_df = pd.DataFrame(X_scaled, columns=self.features)
            probs = self.clf_model.predict_proba(X_df[lr_features])[:, 1]
        else:
            probs = self.clf_model.predict_proba(X_scaled)[:, 1]
            
        # Ensure consistency: If predicted finishing position is > 10, podium probability must be capped close to 0
        for i, row in df.iterrows():
            prob = probs[i]
            if predicted_positions is not None:
                predicted_pos = predicted_positions[i]
            else:
                # Fallback calculation if positions aren't pre-computed
                grid = float(row['grid'])
                predicted_pos = grid # Default fallback
            
            # Capping factor
            if predicted_pos > 3:
                cap_multiplier = np.clip(1.0 - (predicted_pos - 3) / 8.0, 0.0, 1.0)
                # Soft clip probability
                probs[i] = prob * cap_multiplier
                if predicted_pos > 10:
                    probs[i] = min(probs[i], 0.01) # Near zero podium chance if predicted out of top 10

        df['predicted_podium_probability'] = probs
        return df[['driver_id', 'driver_name', 'predicted_podium_probability']].to_dict(orient='records')

    def predict_driver_performance(self, entries: List[Dict[str, Any]], predicted_positions: List[int] = None) -> List[Dict[str, Any]]:
        df, X_scaled = self._prepare_data(entries)
        
        if predicted_positions is None:
            preds_list = self.predict_finish_position(entries)
            predicted_positions = [p['predicted_finishing_position'] for p in preds_list]

        df['predicted_finishing_position'] = predicted_positions
        
        grid_gain = df['grid'] - df['predicted_finishing_position']
        raw_score = 50 + grid_gain * 3 - df['grid_delta_to_avg'] * 2
        df['driver_performance_score'] = np.clip(raw_score, 0, 100).round().astype(int)
        
        return df[['driver_id', 'driver_name', 'driver_performance_score']].to_dict(orient='records')

    def predict_team_performance(self, entries: List[Dict[str, Any]], predicted_positions: List[int] = None) -> List[Dict[str, Any]]:
        df, X_scaled = self._prepare_data(entries)
        
        if predicted_positions is None:
            preds_list = self.predict_finish_position(entries)
            predicted_positions = [p['predicted_finishing_position'] for p in preds_list]

        df['predicted_finishing_position'] = predicted_positions
        
        team_avg = df.groupby('constructor_id')['predicted_finishing_position'].transform('mean')
        df['team_performance_score'] = np.clip(100 - (team_avg - 1) * 5, 0, 100).round().astype(int)
        
        df_teams = df[['constructor_id', 'constructor_name', 'team_performance_score']].drop_duplicates()
        return df_teams.to_dict(orient='records')

    def explain_prediction_local(self, entry: Dict[str, Any], weather: str = "Dry", tyre_compound: str = "Medium") -> Dict[str, Any]:
        """
        Computes SHAP-like contributions, waterfall charts, confidence, and positive/negative factors.
        """
        df, X_scaled = self._prepare_data([entry])
        X_scaled_row = X_scaled[0]

        # 1. Run predictions
        preds_list = self.predict_finish_position([entry])
        predicted_pos = int(preds_list[0]["predicted_finishing_position"])
        predicted_raw = float(preds_list[0]["predicted_raw_score"])

        probs_list = self.predict_podium_probability([entry], [predicted_pos])
        podium_prob = float(probs_list[0]["predicted_podium_probability"])

        # 2. Get global feature importance weights to distribute contribution
        if hasattr(self.reg_model, 'feature_importances_'):
            importances = self.reg_model.feature_importances_
        elif hasattr(self.reg_model, 'coef_'):
            importances = np.abs(self.reg_model.coef_)
            full_importances = []
            coef_idx = 0
            for f in self.features:
                if f in ['grid_delta_to_avg', 'driver_avg_finish']:
                    full_importances.append(0.0)
                else:
                    full_importances.append(importances[coef_idx])
                    coef_idx += 1
            importances = np.array(full_importances)
        else:
            importances = np.ones(len(self.features)) / len(self.features)

        importances /= importances.sum()

        # 3. Calculate local contributions (X_scaled represents distance from mean in standard deviations)
        contributions = {}
        lower_is_better = ['grid', 'driver_recent_form', 'driver_avg_finish', 'driver_consistency', 'driver_rolling_grid', 'grid_delta_to_avg', 'driver_dnf_rate']
        
        for i, feat in enumerate(self.features):
            val = X_scaled_row[i]
            if feat in lower_is_better:
                # If value is lower (better), contribution to success is positive
                cont = -val * importances[i]
            else:
                # If value is higher (better), contribution to success is positive
                cont = val * importances[i]
            contributions[feat] = float(cont)

        # Map to display names
        clean_names = {
            'grid': 'Starting Grid',
            'driver_recent_form': 'Recent Form',
            'constructor_strength_index': 'Team Strength',
            'grid_delta_to_avg': 'Qualifying Overperformance',
            'circuit_grid_importance': 'Track Grid Importance',
            'driver_experience': 'Career Starts',
            'driver_podium_rate': 'Historical Podium Rate',
            'driver_avg_finish': 'Average Finish Position',
            'driver_age': 'Driver Age',
            'circuit_familiarity': 'Track Experience',
            'is_home_race': 'Home Race Advantage',
            'driver_win_rate': 'Historical Win Rate',
            'driver_top10_rate': 'Historical Top 10 Rate',
            'driver_dnf_rate': 'Historical DNF Rate',
            'driver_consistency': 'Consistency Std Dev',
            'driver_rolling_grid': 'Average Starting Grid'
        }

        # Format local contributions for API
        local_cont = {clean_names.get(k, k): round(v * 10, 3) for k, v in contributions.items()}

        # 4. Filter positive/negative factors
        sorted_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        top_pos = [clean_names.get(f[0], f[0]) for f in sorted_factors if f[1] > 0.005][:3]
        top_neg = [clean_names.get(f[0], f[0]) for f in reversed(sorted_factors) if f[1] < -0.005][:3]

        if not top_pos:
            top_pos = ["Qualifying Position"]
        if not top_neg:
            top_neg = ["Grid Position limits"]

        # 5. Build Waterfall Steps
        baseline_val = 11.5
        final_val = float(np.clip(predicted_raw, 1.0, 20.0))
        diff = baseline_val - final_val
        sum_cont = sum(abs(v) for v in contributions.values())
        if sum_cont == 0:
            sum_cont = 1.0

        waterfall_chart = []
        current_val = baseline_val
        waterfall_chart.append({"name": "F1 Grid Baseline", "value": round(current_val, 2), "delta": 0.0})

        # Top 5 features in waterfall, other grouped
        sorted_by_abs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        top_5 = sorted_by_abs[:5]
        others = sorted_by_abs[5:]

        for feat, cont in top_5:
            delta = - (cont / sum_cont) * diff
            current_val += delta
            waterfall_chart.append({
                "name": clean_names.get(feat, feat),
                "delta": round(delta, 2),
                "value": round(current_val, 2)
            })

        # Add Weather and Tyre compound synthetic modifiers to waterfall
        weather_delta = 0.0
        tyre_delta = 0.0
        if weather == "Wet":
            # Rain adds difficulty, increases finish position variance
            weather_delta = 0.4
            current_val += weather_delta
            waterfall_chart.append({"name": "Wet Weather Risk", "delta": round(weather_delta, 2), "value": round(current_val, 2)})
        
        if tyre_compound == "Soft" and entry['grid'] > 10:
            # Soft tyre gives early speed boost to lower grid starts
            tyre_delta = -0.5
            current_val += tyre_delta
            waterfall_chart.append({"name": "Soft Tyre Grid-Gain Boost", "delta": round(tyre_delta, 2), "value": round(current_val, 2)})
        elif tyre_compound == "Hard" and entry['grid'] <= 5:
            # Hard tyres on front starts can drop them initially
            tyre_delta = 0.3
            current_val += tyre_delta
            waterfall_chart.append({"name": "Hard Tyre Start Penalty", "delta": round(tyre_delta, 2), "value": round(current_val, 2)})

        # Remaining features
        other_cont = sum(c[1] for c in others)
        other_delta = - (other_cont / sum_cont) * diff
        current_val += other_delta
        
        # Lock final step to exact prediction
        final_adjustment = final_val + weather_delta + tyre_delta - current_val
        current_val += final_adjustment
        waterfall_chart.append({
            "name": "Other Vehicle Factors",
            "delta": round(other_delta + final_adjustment, 2),
            "value": round(current_val, 2)
        })

        # 6. Confidence Score
        confidence = 65.0 + (podium_prob * 25.0 if podium_prob > 0.5 else (1.0 - podium_prob) * 15.0)
        if entry.get('grid', 10) <= 3:
            confidence += 5.0
        if weather == "Wet":
            confidence -= 10.0 # Rain reduces confidence
        confidence = float(np.clip(confidence, 50.0, 98.0))

        # 7. Generate text explanation
        reasons = []
        if entry['grid'] <= 3:
            reasons.append(f"Front-row start position (P{entry['grid']}) is highly correlated with podium finishes.")
        else:
            reasons.append(f"Starting from grid slot P{entry['grid']} increases the traffic challenge.")

        if entry['constructor_strength_index'] > 20.0:
            reasons.append(f"Strong constructor package score ({entry['constructor_strength_index']:.1f}) provides vehicle stability.")
        
        if entry['driver_recent_form'] < 6.0:
            reasons.append(f"Driver is in peak form, averaging a P{entry['driver_recent_form']:.1f} finish over the last 5 GPs.")
        
        if weather == "Wet":
            reasons.append("Wet conditions increase DNF probability and introduce high race pace variability.")
        if tyre_compound == "Soft":
            reasons.append("Soft tyres provide high early traction for overtakes but require careful stint management.")

        explanation = f"Predicted to finish in P{predicted_pos} with a {podium_prob*100:.1f}% podium chance. Reasons include:\n" + "\n".join([f"- {r}" for r in reasons])

        # Compute radar metrics on a 0-100 scale for visual rendering
        recent_form_val = float(entry.get('driver_recent_form', 5.0))
        team_strength_val = float(entry.get('constructor_strength_index', 20.0))
        grid_delta_val = float(entry.get('grid_delta_to_avg', 0.0))
        podium_rate_val = float(entry.get('driver_podium_rate', 0.15))
        circuit_familiarity_val = float(entry.get('circuit_familiarity', 5.0))

        radar_metrics = {
            "Driver Skill": float(np.clip(podium_rate_val * 100.0, 10.0, 100.0)),
            "Recent Form": float(np.clip(100.0 - (recent_form_val - 1.0) * 5.0, 10.0, 100.0)),
            "Constructor Strength": float(np.clip(team_strength_val * 2.0, 10.0, 100.0)),
            "Qualifying Pace": float(np.clip(50.0 - (grid_delta_val * 10.0), 10.0, 100.0)),
            "Circuit Familiarity": float(np.clip(circuit_familiarity_val * 8.0, 10.0, 100.0))
        }

        return {
            "shap_importance": {clean_names.get(k, k): abs(v) for k, v in contributions.items()},
            "local_contributions": local_cont,
            "waterfall_chart": waterfall_chart,
            "top_positive_factors": top_pos,
            "top_negative_factors": top_neg,
            "confidence_score": round(confidence, 1),
            "explanation": explanation,
            "radar_metrics": radar_metrics
        }
