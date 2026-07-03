import React, { useState } from 'react';
import { predictionApi } from '../services/api';
import { FiTrendingUp, FiSettings, FiActivity, FiAward, FiAlertCircle } from 'react-icons/fi';

const DEFAULT_DRIVERS = [
  {
    driver_id: 1,
    driver_name: "Lewis Hamilton",
    constructor_id: 131,
    constructor_name: "Mercedes",
    grid: 1,
    driver_age: 36.2,
    driver_experience: 266,
    driver_recent_form: 2.2,
    driver_rolling_grid: 1.8,
    driver_avg_finish: 3.4,
    driver_consistency: 4.1,
    driver_win_rate: 0.35,
    driver_podium_rate: 0.61,
    driver_top10_rate: 0.88,
    driver_dnf_rate: 0.08,
    grid_delta_to_avg: -0.8,
    constructor_strength_index: 39.7,
    circuit_familiarity: 14,
    circuit_grid_importance: 0.60,
    is_home_race: 0
  },
  {
    driver_id: 830,
    driver_name: "Max Verstappen",
    constructor_id: 9,
    constructor_name: "Red Bull",
    grid: 2,
    driver_age: 23.5,
    driver_experience: 119,
    driver_recent_form: 2.0,
    driver_rolling_grid: 2.5,
    driver_avg_finish: 5.2,
    driver_consistency: 4.8,
    driver_win_rate: 0.12,
    driver_podium_rate: 0.38,
    driver_top10_rate: 0.72,
    driver_dnf_rate: 0.15,
    grid_delta_to_avg: -0.5,
    constructor_strength_index: 29.3,
    circuit_familiarity: 6,
    circuit_grid_importance: 0.60,
    is_home_race: 0
  },
  {
    driver_id: 822,
    driver_name: "Valtteri Bottas",
    constructor_id: 131,
    constructor_name: "Mercedes",
    grid: 3,
    driver_age: 31.6,
    driver_experience: 156,
    driver_recent_form: 4.1,
    driver_rolling_grid: 3.2,
    driver_avg_finish: 6.8,
    driver_consistency: 4.5,
    driver_win_rate: 0.06,
    driver_podium_rate: 0.32,
    driver_top10_rate: 0.78,
    driver_dnf_rate: 0.10,
    grid_delta_to_avg: 0.2,
    constructor_strength_index: 39.7,
    circuit_familiarity: 8,
    circuit_grid_importance: 0.60,
    is_home_race: 0
  },
  {
    driver_id: 815,
    driver_name: "Sergio Pérez",
    constructor_id: 9,
    constructor_name: "Red Bull",
    grid: 4,
    driver_age: 31.2,
    driver_experience: 191,
    driver_recent_form: 6.2,
    driver_rolling_grid: 5.8,
    driver_avg_finish: 9.2,
    driver_consistency: 4.8,
    driver_win_rate: 0.02,
    driver_podium_rate: 0.12,
    driver_top10_rate: 0.68,
    driver_dnf_rate: 0.14,
    grid_delta_to_avg: 0.4,
    constructor_strength_index: 29.3,
    circuit_familiarity: 10,
    circuit_grid_importance: 0.60,
    is_home_race: 0
  },
  {
    driver_id: 846,
    driver_name: "Lando Norris",
    constructor_id: 1,
    constructor_name: "McLaren",
    grid: 5,
    driver_age: 21.4,
    driver_experience: 38,
    driver_recent_form: 5.8,
    driver_rolling_grid: 6.2,
    driver_avg_finish: 10.4,
    driver_consistency: 4.6,
    driver_win_rate: 0.00,
    driver_podium_rate: 0.05,
    driver_top10_rate: 0.62,
    driver_dnf_rate: 0.12,
    grid_delta_to_avg: -0.4,
    constructor_strength_index: 18.2,
    circuit_familiarity: 2,
    circuit_grid_importance: 0.60,
    is_home_race: 0
  }
];

export default function Predictions() {
  const [entries, setEntries] = useState(DEFAULT_DRIVERS);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGridChange = (driverId, newGrid) => {
    const val = parseInt(newGrid);
    setEntries(prev => prev.map(item => {
      if (item.driver_id === driverId) {
        // Calculate new grid delta
        const delta = val - item.driver_rolling_grid;
        return { ...item, grid: val, grid_delta_to_avg: parseFloat(delta.toFixed(1)) };
      }
      return item;
    }));
  };

  const handlePredict = () => {
    setLoading(true);
    setError(null);
    const payload = {
      race_id: 1051,
      entries: entries
    };

    Promise.all([
      predictionApi.getFinishPosition(payload),
      predictionApi.getPodiumProbability(payload),
      predictionApi.getDriverPerformance(payload),
      predictionApi.getTeamPerformance(payload)
    ])
      .then(([finishRes, probRes, driverRes, teamRes]) => {
        // Merge results by driver_id
        const merged = entries.map(driver => {
          const fObj = finishRes.predictions.find(p => p.driver_id === driver.driver_id);
          const pObj = probRes.predictions.find(p => p.driver_id === driver.driver_id);
          const dObj = driverRes.predictions.find(p => p.driver_id === driver.driver_id);
          const tObj = teamRes.predictions.find(p => p.constructor_id === driver.constructor_id);
          
          return {
            driver_name: driver.driver_name,
            constructor_name: driver.constructor_name,
            grid: driver.grid,
            predicted_finishing_position: fObj ? fObj.predicted_finishing_position : 99,
            predicted_podium_probability: pObj ? pObj.predicted_podium_probability : 0.0,
            driver_performance_score: dObj ? dObj.driver_performance_score : 50,
            team_performance_score: tObj ? tObj.team_performance_score : 50,
          };
        }).sort((a, b) => a.predicted_finishing_position - b.predicted_finishing_position);
        
        setPredictions(merged);
        
        // Cache to localStorage for sharing with the Model Performance page
        const lastPredictionData = {
          source: 'predictions_center',
          timestamp: new Date().toLocaleString(),
          circuit_name: 'Monaco GP', // Default Monaco GP track in predictions center
          season: 2021,
          drivers: merged.map(p => {
            const orig = entries.find(e => e.driver_name === p.driver_name);
            return {
              ...p,
              driver_recent_form: orig ? orig.driver_recent_form : 5.0,
              constructor_strength_index: orig ? orig.constructor_strength_index : 20.0,
              grid_delta_to_avg: orig ? orig.grid_delta_to_avg : 0.0,
              circuit_grid_importance: orig ? orig.circuit_grid_importance : 0.60,
              circuit_familiarity: orig ? orig.circuit_familiarity : 5,
            };
          })
        };
        localStorage.setItem('racevision_last_prediction', JSON.stringify(lastPredictionData));
        
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Prediction execution failed.');
        setLoading(false);
      });
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-wide">AI Predictions Center</h2>
        <p className="text-gray-400 text-sm">Configure starting grid options to run live motorsport predictive analytics.</p>
      </div>

      {/* Grid Inputs configuration */}
      <div className="glass-card p-6 space-y-6">
        <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3">
          1. Configure Race Grid
        </h3>
        
        <div className="space-y-4">
          {entries.map(driver => (
            <div key={driver.driver_id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-[#111216]/40 border border-[#2D3139]/40 rounded-lg gap-4">
              <div>
                <span className="font-semibold text-white text-sm block">{driver.driver_name}</span>
                <span className="text-xs text-gray-500">{driver.constructor_name}</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <label className="text-xs text-gray-400 font-semibold uppercase">Starting Grid:</label>
                <select 
                  className="bg-[#181A20] border border-[#2D3139] rounded px-3 py-1.5 text-white focus:outline-none focus:border-accentGreen text-sm"
                  value={driver.grid}
                  onChange={(e) => handleGridChange(driver.driver_id, e.target.value)}
                >
                  {[...Array(20)].map((_, i) => (
                    <option key={i+1} value={i+1}>P{i+1}</option>
                  ))}
                </select>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end pt-4">
          <button 
            className={`
              px-6 py-2.5 bg-gradient-to-r from-accentGreen to-accentBlue text-darkBg font-bold rounded-lg hover:opacity-90 transition-opacity flex items-center space-x-2
              ${loading ? 'opacity-50 cursor-wait' : ''}
            `}
            onClick={handlePredict}
            disabled={loading}
          >
            <FiTrendingUp />
            <span>{loading ? 'Running ML Inference...' : 'Calculate Grid Predictions'}</span>
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-[#FF4A6B]/10 border border-[#FF4A6B]/30 rounded-xl p-4 flex items-center space-x-3 text-accentRed">
          <FiAlertCircle size={20} />
          <span className="text-sm font-medium">{error}</span>
        </div>
      )}

      {/* Predictions Output list */}
      {predictions && (
        <div className="glass-card p-6 space-y-6">
          <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3">
            2. Predict Forecast Results
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#111216]/50 border-b border-[#2D3139]">
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400">Driver</th>
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400 text-center">Start Grid</th>
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400 text-center">Predict Finish</th>
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400">Podium Likelihood</th>
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400 text-center">Driver Index</th>
                  <th className="px-6 py-3 text-xs font-bold uppercase tracking-wider text-gray-400 text-center">Constructor Strength</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#2D3139]/40">
                {predictions.map((p, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors duration-150">
                    <td className="px-6 py-4">
                      <span className="font-semibold text-white text-sm block">{p.driver_name}</span>
                      <span className="text-xs text-gray-500">{p.constructor_name}</span>
                    </td>
                    <td className="px-6 py-4 text-center font-medium text-gray-300">P{p.grid}</td>
                    <td className="px-6 py-4 text-center">
                      <span className={`
                        inline-block px-2.5 py-1 rounded text-xs font-bold
                        ${p.predicted_finishing_position <= 3 ? 'bg-[#FFC837]/15 text-[#FFC837]' : 'bg-gray-700/30 text-gray-300'}
                      `}>
                        P{p.predicted_finishing_position}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-white w-10">{(p.predicted_podium_probability * 100).toFixed(0)}%</span>
                        <div className="w-24 bg-gray-700 h-2 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${p.predicted_podium_probability >= 0.5 ? 'bg-accentGreen' : p.predicted_podium_probability >= 0.2 ? 'bg-accentYellow' : 'bg-accentRed'}`}
                            style={{ width: `${p.predicted_podium_probability * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center font-bold text-[#00F29E]">{p.driver_performance_score}</td>
                    <td className="px-6 py-4 text-center font-bold text-[#00D4FF]">{p.team_performance_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
