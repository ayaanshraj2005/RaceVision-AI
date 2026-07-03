import React, { useState, useEffect } from 'react';
import { explainApi, analyticsApi } from '../services/api';
import { FiCpu, FiMessageSquare, FiTrendingUp, FiActivity, FiUser, FiCalendar } from 'react-icons/fi';

export default function XAI() {
  // Seasons and drivers dropdown lists
  const [seasons, setSeasons] = useState([]);
  const [season, setSeason] = useState(2021); // Default season
  const [drivers, setDrivers] = useState([]);
  
  // Telemetry Input state
  const [driverName, setDriverName] = useState('Lewis Hamilton');
  const [constructorName, setConstructorName] = useState('Mercedes');
  const [grid, setGrid] = useState(1);
  const [recentForm, setRecentForm] = useState(2.2);
  const [teamScore, setTeamScore] = useState(39.7);
  const [gridDelta, setGridDelta] = useState(-0.8);
  const [corr, setCorr] = useState(0.60);
  const [circuitName, setCircuitName] = useState('Monaco GP');

  // Backend response / details state
  const [details, setDetails] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [predPos, setPredPos] = useState(null);
  const [predProb, setPredProb] = useState(null);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState(null);

  // 1. Initial Load of Seasons
  useEffect(() => {
    analyticsApi.getSeasons()
      .then(res => {
        const years = res.map(s => s.year).sort((a, b) => b - a); // descending order
        setSeasons(years);
        if (years.length > 0) {
          const defaultSeason = years.includes(2021) ? 2021 : years[0];
          setSeason(defaultSeason);
          loadDriversForSeason(defaultSeason, 'Lewis Hamilton');
        } else {
          loadDriversForSeason(2021, 'Lewis Hamilton');
        }
      })
      .catch(err => {
        console.error("Failed to load seasons", err);
        loadDriversForSeason(2021, 'Lewis Hamilton');
      });
  }, []);

  // Helper: Load drivers list for a given season
  const loadDriversForSeason = (selectedSeason, targetDriver = null) => {
    setLoadingDetails(true);
    explainApi.getDriversList(selectedSeason)
      .then(driverList => {
        setDrivers(driverList);
        // Determine which driver to load details for
        let activeDriver = targetDriver;
        if (!activeDriver || !driverList.includes(activeDriver)) {
          activeDriver = driverList.includes('Lewis Hamilton') ? 'Lewis Hamilton' : driverList[0];
        }
        if (activeDriver) {
          setDriverName(activeDriver);
          loadDriverDetails(activeDriver, selectedSeason);
        } else {
          setLoadingDetails(false);
        }
      })
      .catch(err => {
        setError(err.message || 'Failed to load drivers for this season.');
        setLoadingDetails(false);
      });
  };

  // Helper: Fetch and update driver details
  const loadDriverDetails = (driver, selectedSeason) => {
    setLoadingDetails(true);
    setError(null);
    explainApi.getDriverDetails(driver, selectedSeason)
      .then(res => {
        setDetails(res);
        setConstructorName(res.team);
        setRecentForm(res.recent_form);
        setTeamScore(res.team_strength);
        setGridDelta(res.grid_delta_to_avg);
        setLoadingDetails(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch driver telemetry details.');
        setLoadingDetails(false);
      });
  };

  // Change handlers
  const handleSeasonChange = (newSeason) => {
    setSeason(newSeason);
    loadDriversForSeason(newSeason, driverName);
  };

  const handleDriverChange = (newDriver) => {
    setDriverName(newDriver);
    loadDriverDetails(newDriver, season);
  };

  const handleExplain = () => {
    setLoading(true);
    setError(null);
    const payload = {
      driver_name: driverName,
      constructor_name: constructorName,
      grid: parseInt(grid),
      driver_recent_form: parseFloat(recentForm),
      constructor_strength_index: parseFloat(teamScore),
      grid_delta_to_avg: parseFloat(gridDelta),
      circuit_grid_importance: parseFloat(corr),
      circuit_name: circuitName,
      season: parseInt(season)
    };

    explainApi.explainPrediction(payload)
      .then(res => {
        setExplanation(res.explanation);
        setPredPos(res.predicted_finishing_position);
        setPredProb(res.predicted_podium_probability);
        
        // Cache to localStorage for sharing with the Model Performance page
        const lastPredictionData = {
          source: 'explainable_ai',
          timestamp: new Date().toLocaleString(),
          circuit_name: circuitName,
          season: season,
          driver_name: driverName,
          constructor_name: constructorName,
          grid: parseInt(grid),
          driver_recent_form: parseFloat(recentForm),
          constructor_strength_index: parseFloat(teamScore),
          grid_delta_to_avg: parseFloat(gridDelta),
          circuit_grid_importance: parseFloat(corr),
          predicted_finishing_position: res.predicted_finishing_position,
          predicted_podium_probability: res.predicted_podium_probability,
          explanation: res.explanation,
          confidence_score: res.confidence_score,
          top_positive_factors: res.top_positive_factors,
          top_negative_factors: res.top_negative_factors,
          local_contributions: res.local_contributions,
          radar_metrics: res.radar_metrics
        };
        localStorage.setItem('racevision_last_prediction', JSON.stringify(lastPredictionData));
        
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to execute prediction explanation.');
        setLoading(false);
      });
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-wide">Explainable AI (XAI) Dashboard</h2>
        <p className="text-gray-400 text-sm">Translate complex model weights into transparent, human-readable race insights.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Input parameters panel */}
        <div className="glass-card p-6 space-y-6 relative overflow-hidden">
          {/* Glass Loading overlay */}
          {loadingDetails && (
            <div className="absolute inset-0 bg-[#0F1115]/80 flex items-center justify-center z-10 transition-opacity">
              <div className="flex flex-col items-center space-y-3">
                <div className="w-10 h-10 border-4 border-accentGreen border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs font-semibold text-accentGreen uppercase tracking-wider animate-pulse">Syncing Telemetry...</span>
              </div>
            </div>
          )}

          <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3 flex items-center space-x-2">
            <FiCpu className="text-accentGreen" />
            <span>1. Set Telemetry Parameters</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Season Selector */}
            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1 flex items-center space-x-1">
                <FiCalendar className="text-gray-500" />
                <span>Season (Year)</span>
              </label>
              <select 
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={season}
                onChange={e => handleSeasonChange(parseInt(e.target.value))}
              >
                {seasons.map(yr => (
                  <option key={yr} value={yr}>{yr} Season</option>
                ))}
              </select>
            </div>

            {/* Driver Dropdown Selector */}
            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1 flex items-center space-x-1">
                <FiUser className="text-gray-500" />
                <span>Driver Name</span>
              </label>
              <select 
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={driverName}
                onChange={e => handleDriverChange(e.target.value)}
              >
                {drivers.map(drv => (
                  <option key={drv} value={drv}>{drv}</option>
                ))}
              </select>
            </div>

            {/* Team Name Input (Read-only / Disabled) */}
            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Team Name</label>
              <input 
                className="w-full bg-[#111216]/50 border border-[#2D3139] rounded px-3 py-1.5 text-gray-400 text-sm cursor-not-allowed focus:outline-none"
                value={constructorName}
                readOnly
                disabled
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Starting Grid</label>
              <select 
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={grid}
                onChange={e => setGrid(e.target.value)}
              >
                {[...Array(20)].map((_, i) => (
                  <option key={i+1} value={i+1}>P{i+1}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Driver Recent Form (avg finish)</label>
              <input 
                type="number" step="0.1"
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={recentForm}
                onChange={e => setRecentForm(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Team strength Index (points avg)</label>
              <input 
                type="number" step="0.5"
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={teamScore}
                onChange={e => setTeamScore(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Grid Delta to Avg Grid</label>
              <input 
                type="number" step="0.1"
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={gridDelta}
                onChange={e => setGridDelta(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Circuit Grid Correlation</label>
              <input 
                type="number" step="0.05"
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={corr}
                onChange={e => setCorr(e.target.value)}
              />
            </div>

            <div className="sm:col-span-2">
              <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Circuit Name</label>
              <input 
                className="w-full bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white text-sm focus:outline-none focus:border-accentGreen"
                value={circuitName}
                onChange={e => setCircuitName(e.target.value)}
              />
            </div>
          </div>

          {/* Driver & Constructor Profiling display */}
          {details && (
            <div className="bg-[#111216]/40 border border-[#2D3139]/40 rounded-lg p-4 space-y-3 transition-all duration-300">
              <span className="text-xs text-[#00F29E] font-bold uppercase tracking-wider block border-b border-[#2D3139]/40 pb-1.5 flex items-center space-x-1.5">
                <FiActivity className="animate-pulse text-[#00F29E]" />
                <span>Backend Telemetry Insights ({season})</span>
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-gray-500 block mb-0.5">Driver Age</span>
                  <span className="font-semibold text-white">{details.age ? details.age.toFixed(1) : 'N/A'} yrs</span>
                </div>
                <div>
                  <span className="text-gray-500 block mb-0.5">Career Starts</span>
                  <span className="font-semibold text-white">{details.experience ?? 'N/A'} GPs</span>
                </div>
                <div>
                  <span className="text-gray-500 block mb-0.5">Historical Win Rate</span>
                  <span className="font-semibold text-white">{details.historical_win_rate ? (details.historical_win_rate * 100).toFixed(1) + '%' : '0.0%'}</span>
                </div>
                <div>
                  <span className="text-gray-500 block mb-0.5">Constructor Strength</span>
                  <span className="font-semibold text-white">{details.team_strength ? details.team_strength.toFixed(1) : 'N/A'}</span>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end pt-4">
            <button 
              className={`
                px-6 py-2 bg-gradient-to-r from-accentGreen to-accentBlue text-darkBg font-bold rounded-lg hover:opacity-90 transition-opacity flex items-center space-x-2
                ${loading ? 'opacity-50 cursor-wait' : ''}
              `}
              onClick={handleExplain}
              disabled={loading || loadingDetails}
            >
              <FiMessageSquare />
              <span>{loading ? 'Running Explainability Engine...' : 'Analyze Forecast Decisions'}</span>
            </button>
          </div>
        </div>

        {/* Right: Explanations console output */}
        <div className="glass-card p-6 flex flex-col justify-between min-h-[400px]">
          <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3 flex items-center space-x-2">
            <FiMessageSquare className="text-accentBlue" />
            <span>2. Transparent Explanation Output</span>
          </h3>

          <div className="flex-1 my-6 flex flex-col justify-center">
            {explanation ? (
              <div className="space-y-6">
                {/* Result header */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#111216] p-4 rounded-lg border border-[#2D3139]/40 text-center">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Predicted Rank</span>
                    <span className="text-2xl font-black text-[#00F29E] mt-1">P{predPos}</span>
                  </div>
                  <div className="bg-[#111216] p-4 rounded-lg border border-[#2D3139]/40 text-center">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Podium Chance</span>
                    <span className="text-2xl font-black text-[#00D4FF] mt-1">{(predProb * 100).toFixed(0)}%</span>
                  </div>
                </div>
                
                {/* Detailed explanation console */}
                <div className="bg-[#111216] border border-[#2D3139] rounded-lg p-5 font-mono text-xs text-gray-300 leading-relaxed whitespace-pre-line">
                  {explanation}
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-12">
                <FiCpu className="mx-auto text-4xl mb-4 opacity-40 animate-pulse" />
                <p className="text-sm">Configure telemetry values and click analyze to see decision factors.</p>
              </div>
            )}

            {error && (
              <div className="mt-4 bg-[#FF4A6B]/15 border border-[#FF4A6B]/30 rounded-lg p-4 text-accentRed text-xs font-medium">
                {error}
              </div>
            )}
          </div>

          <div className="text-xs text-gray-500 text-center pt-2">
            Decisions decomposed dynamically using local contribution weights.
          </div>
        </div>
      </div>
    </div>
  );
}
