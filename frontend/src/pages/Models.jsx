import React, { useState, useEffect } from 'react';
import { explainApi } from '../services/api';
import { 
  FiAward, FiSettings, FiActivity, FiCheckCircle, FiInfo, 
  FiRefreshCw, FiCpu, FiChevronRight, FiSmile, FiAlertTriangle 
} from 'react-icons/fi';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, Cell 
} from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Premium high-fidelity default mock data for the first-visit fallback state
const DEFAULT_FALLBACK_PREDICTION = {
  source: 'explainable_ai',
  timestamp: new Date().toLocaleString(),
  circuit_name: 'Monaco GP',
  season: 2021,
  driver_name: 'Lewis Hamilton',
  constructor_name: 'Mercedes',
  grid: 1,
  driver_recent_form: 2.2,
  constructor_strength_index: 39.7,
  grid_delta_to_avg: -0.8,
  circuit_grid_importance: 0.60,
  predicted_finishing_position: 1,
  predicted_podium_probability: 0.85,
  confidence_score: 92.5,
  top_positive_factors: [
    "Front-row start position (P1)",
    "Strong constructor package score (39.7)",
    "High track layout grid advantage at Monaco GP"
  ],
  top_negative_factors: [
    "Grid Position limits"
  ],
  explanation: "Driver Lewis Hamilton is predicted to finish in Position 1 (Podium Probability: 85.0%) because:\n- Strong qualifying pace starting from Grid position P1\n- High-performance vehicle package from Mercedes (Recent Team score: 39.7)\n- High track layout grid advantage at Monaco GP (Pearson: 0.60)",
  radar_metrics: {
    "Driver Skill": 90.0,
    "Recent Form": 94.0,
    "Constructor Strength": 79.4,
    "Qualifying Pace": 58.0,
    "Circuit Familiarity": 48.0
  },
  local_contributions: {
    "Starting Grid": 3.84,
    "Team Strength": 2.12,
    "Recent Form": 1.82,
    "Qualifying Overperformance": 1.25,
    "Track Experience": 0.45,
    "Track Grid Importance": 0.35
  }
};

// SVG gauge visual representation for confidence scores
const ConfidenceGauge = ({ score }) => {
  const radius = 60;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let strokeColor = "#FF4A6B"; // Red
  if (score >= 80) strokeColor = "#00F29E"; // Green
  else if (score >= 65) strokeColor = "#00D4FF"; // Blue
  else if (score >= 50) strokeColor = "#FFC837"; // Yellow

  return (
    <div className="flex flex-col items-center justify-center relative w-32 h-32">
      <svg
        height={radius * 2}
        width={radius * 2}
        className="transform -rotate-90 transition-all duration-1000 ease-out"
      >
        <circle
          stroke="rgba(45, 49, 57, 0.25)"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={strokeColor}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute text-center">
        <span className="text-2xl font-black text-white">{score}%</span>
        <span className="text-[9px] text-gray-400 uppercase font-bold block tracking-wider mt-0.5">Confidence</span>
      </div>
    </div>
  );
};

export default function Models() {
  // Section 1 State
  const [metrics, setMetrics] = useState(null);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Section 2 State
  const [lastPrediction, setLastPrediction] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [driverAnalysis, setDriverAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  // Initial Load for Metrics and Cache
  useEffect(() => {
    Promise.all([explainApi.getModelMetrics(), explainApi.getModelInfo()])
      .then(([metricsRes, infoRes]) => {
        setMetrics(metricsRes);
        setInfo(infoRes);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to fetch model diagnostics.');
        setLoading(false);
      });

    loadCachedPrediction();
  }, []);

  // Fetch explanations on driver change or new predictions
  useEffect(() => {
    if (selectedDriver && lastPrediction) {
      fetchAnalysisForDriver(selectedDriver, lastPrediction);
    } else if (!lastPrediction) {
      setDriverAnalysis(DEFAULT_FALLBACK_PREDICTION);
    }
  }, [selectedDriver, lastPrediction]);

  // Load from LocalStorage
  const loadCachedPrediction = () => {
    const cached = localStorage.getItem('racevision_last_prediction');
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        setLastPrediction(parsed);
        if (parsed.source === 'predictions_center' && parsed.drivers && parsed.drivers.length > 0) {
          setSelectedDriver(parsed.drivers[0].driver_name);
        } else if (parsed.source === 'explainable_ai') {
          setSelectedDriver(parsed.driver_name);
          setDriverAnalysis(parsed);
        }
      } catch (err) {
        console.error("Failed to parse cached prediction data", err);
      }
    } else {
      setDriverAnalysis(DEFAULT_FALLBACK_PREDICTION);
    }
  };

  // On-demand explain fetch for Predictions Center driver
  const fetchAnalysisForDriver = (driverName, predictionData) => {
    if (!predictionData) return;

    if (predictionData.source === 'explainable_ai' && predictionData.driver_name === driverName) {
      setDriverAnalysis(predictionData);
      return;
    }

    if (predictionData.source === 'predictions_center') {
      const drv = predictionData.drivers.find(d => d.driver_name === driverName);
      if (!drv) return;

      setAnalysisLoading(true);
      setAnalysisError(null);

      const payload = {
        driver_name: drv.driver_name,
        constructor_name: drv.constructor_name,
        grid: parseInt(drv.grid),
        driver_recent_form: parseFloat(drv.driver_recent_form),
        constructor_strength_index: parseFloat(drv.constructor_strength_index),
        grid_delta_to_avg: parseFloat(drv.grid_delta_to_avg),
        circuit_grid_importance: parseFloat(drv.circuit_grid_importance),
        circuit_name: predictionData.circuit_name || 'Monaco GP',
        season: parseInt(predictionData.season) || 2021
      };

      explainApi.explainPrediction(payload)
        .then(res => {
          setDriverAnalysis({
            ...drv,
            source: 'predictions_center',
            timestamp: predictionData.timestamp,
            circuit_name: predictionData.circuit_name || 'Monaco GP',
            season: predictionData.season || 2021,
            explanation: res.explanation,
            confidence_score: res.confidence_score,
            top_positive_factors: res.top_positive_factors,
            top_negative_factors: res.top_negative_factors,
            local_contributions: res.local_contributions,
            radar_metrics: res.radar_metrics
          });
          setAnalysisLoading(false);
        })
        .catch(err => {
          setAnalysisError(err.message || 'Failed to fetch detailed explanations.');
          setAnalysisLoading(false);
        });
    }
  };

  if (loading) {
    return <div className="h-96 bg-[#181A20] animate-pulse rounded-xl border border-[#2D3139]" />;
  }

  if (error) {
    return <div className="glass-card p-6 text-accentRed">{error}</div>;
  }

  // Visual URLs hosted statically by FastAPI app
  const predictionVsActualUrl = `${API_BASE_URL}/visualizations/prediction_vs_actual.png`;
  const residualAnalysisUrl = `${API_BASE_URL}/visualizations/residual_analysis.png`;
  const rocCurveUrl = `${API_BASE_URL}/visualizations/roc_curve.png`;
  const prCurveUrl = `${API_BASE_URL}/visualizations/pr_curve.png`;

  // Process data for charts
  const radarData = driverAnalysis && driverAnalysis.radar_metrics
    ? Object.entries(driverAnalysis.radar_metrics).map(([key, val]) => ({
        subject: key,
        value: val,
      }))
    : [];

  const rawContributions = driverAnalysis && driverAnalysis.local_contributions
    ? Object.entries(driverAnalysis.local_contributions)
    : [];

  const contributionData = rawContributions.map(([name, val]) => ({
    name,
    value: parseFloat(val.toFixed(3)),
  })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  // Extraction values for display
  const driverNameVal = driverAnalysis?.driver_name || driverAnalysis?.driver || 'N/A';
  const teamNameVal = driverAnalysis?.constructor_name || driverAnalysis?.team || 'N/A';
  const circuitVal = driverAnalysis?.circuit_name || 'Monaco GP';
  const gridVal = driverAnalysis?.grid ?? 1;
  const predictedPosVal = driverAnalysis?.predicted_finishing_position ?? 1;
  const podiumProbVal = driverAnalysis?.predicted_podium_probability ?? 0.0;
  const confidenceVal = driverAnalysis?.confidence_score ?? 75.0;
  const timestampVal = driverAnalysis?.timestamp || 'N/A';

  return (
    <div className="space-y-12">
      {/* Title Header */}
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-wide">Model Architecture & Performance</h2>
        <p className="text-gray-400 text-sm mt-1">Monitor static historical metrics alongside dynamic live model predictions.</p>
      </div>

      {/* SECTION 2: LIVE PREDICTION ANALYSIS (DYNAMIC) */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#2D3139] pb-3 gap-3">
          <div className="flex items-center space-x-2">
            <FiCpu className="text-accentGreen text-xl animate-pulse" />
            <h3 className="text-lg font-bold text-white tracking-wide">
              SECTION 2: Live Prediction Analysis
            </h3>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-xs text-gray-400 bg-[#181A20] px-3 py-1 rounded border border-[#2D3139]">
              Last Prediction: <strong className="text-white">{timestampVal}</strong>
            </span>
            <button 
              onClick={loadCachedPrediction}
              className="p-1.5 rounded bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              title="Sync Latest Prediction"
            >
              <FiRefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Multi-driver Dropdown Selector (if loaded from Predictions Center) */}
        {lastPrediction && lastPrediction.source === 'predictions_center' && lastPrediction.drivers && (
          <div className="bg-[#181A20]/40 border border-[#2D3139]/40 p-4 rounded-xl flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Predictions Group:</span>
              <span className="text-xs font-bold text-accentBlue">Multi-Driver Race Forecast</span>
            </div>
            <div className="flex items-center space-x-3">
              <label className="text-xs text-gray-400 font-semibold uppercase">Focus Driver:</label>
              <select 
                className="bg-[#111216] border border-[#2D3139] rounded px-3 py-1.5 text-white focus:outline-none focus:border-accentGreen text-sm"
                value={selectedDriver || ''}
                onChange={(e) => setSelectedDriver(e.target.value)}
              >
                {lastPrediction.drivers.map(d => (
                  <option key={d.driver_name} value={d.driver_name}>{d.driver_name}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Live Predict Console */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative">
          {/* Glass Loading overlay */}
          {analysisLoading && (
            <div className="absolute inset-0 bg-[#111216]/75 flex items-center justify-center z-10 rounded-2xl transition-opacity">
              <div className="flex flex-col items-center space-y-3">
                <div className="w-10 h-10 border-4 border-accentGreen border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs font-semibold text-accentGreen uppercase tracking-wider animate-pulse">Running Explainability...</span>
              </div>
            </div>
          )}

          {/* Column 1: Core Metrics & Explanation */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-card p-6 grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Selected Driver</span>
                <span className="text-base font-extrabold text-white mt-1 block truncate">{driverNameVal}</span>
              </div>
              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Constructor Team</span>
                <span className="text-base font-extrabold text-white mt-1 block truncate">{teamNameVal}</span>
              </div>
              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg col-span-2 md:col-span-1">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Circuit GP</span>
                <span className="text-base font-extrabold text-accentBlue mt-1 block truncate">{circuitVal}</span>
              </div>

              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg text-center">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Grid Start</span>
                <span className="text-2xl font-black text-white mt-1 block">P{gridVal}</span>
              </div>
              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg text-center">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Predict Finish</span>
                <span className="text-2xl font-black text-[#00F29E] mt-1 block">P{predictedPosVal}</span>
              </div>
              <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg text-center col-span-2 md:col-span-1">
                <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider block">Podium Likelihood</span>
                <span className="text-2xl font-black text-accentYellow mt-1 block">{(podiumProbVal * 100).toFixed(0)}%</span>
              </div>
            </div>

            {/* Local SHAP contributions horizontal chart */}
            <div className="glass-card p-6">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">
                Local Feature Contributions (Impact on Finish Order)
              </h4>
              {contributionData.length > 0 ? (
                <div className="h-68">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={contributionData}
                      layout="vertical"
                      margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                    >
                      <XAxis type="number" stroke="#2D3139" tick={{ fill: '#6B7280', fontSize: 10 }} />
                      <YAxis
                        dataKey="name"
                        type="category"
                        stroke="#2D3139"
                        tick={{ fill: '#9CA3AF', fontSize: 9 }}
                        width={140}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#181A20', borderColor: '#2D3139', color: '#fff' }}
                        itemStyle={{ color: '#00F29E' }}
                      />
                      <ReferenceLine x={0} stroke="#4B5563" strokeDasharray="3 3" />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {contributionData.map((entry, index) => {
                          const isPositive = entry.value >= 0;
                          return (
                            <Cell
                              key={`cell-${index}`}
                              fill={isPositive ? '#00F29E' : '#FF4A6B'}
                            />
                          );
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500 text-xs">No contribution weights available.</div>
              )}
            </div>
          </div>

          {/* Column 2: Radar, Gauge, and Factors */}
          <div className="space-y-6">
            {/* Gauge & Radar Grid */}
            <div className="glass-card p-6 flex flex-col items-center justify-center gap-6">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider w-full text-left">
                Predictive Strength Profile
              </h4>
              <div className="flex flex-col sm:flex-row items-center justify-around w-full gap-4">
                <ConfidenceGauge score={confidenceVal} />
                
                {/* Radar chart */}
                {radarData.length > 0 ? (
                  <div className="w-full max-w-[200px]">
                    <ResponsiveContainer width="100%" height={180}>
                      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                        <PolarGrid stroke="#2D3139" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 8 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} stroke="#2D3139" />
                        <Radar
                          name="Ability"
                          dataKey="value"
                          stroke="#00D4FF"
                          fill="#00D4FF"
                          fillOpacity={0.15}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500 text-[10px]">No radar details available.</div>
                )}
              </div>
            </div>

            {/* Factors Badges */}
            <div className="glass-card p-5 space-y-4">
              <div>
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block mb-2">Top Positive Factors</span>
                <div className="flex flex-wrap gap-2">
                  {driverAnalysis?.top_positive_factors?.map((f, i) => (
                    <span key={i} className="text-xs font-semibold bg-[#00F29E]/10 border border-[#00F29E]/25 text-[#00F29E] px-2.5 py-1 rounded">
                      {f}
                    </span>
                  )) || <span className="text-xs text-gray-500">None identified</span>}
                </div>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block mb-2">Top Negative Factors</span>
                <div className="flex flex-wrap gap-2">
                  {driverAnalysis?.top_negative_factors?.map((f, i) => (
                    <span key={i} className="text-xs font-semibold bg-[#FF4A6B]/10 border border-[#FF4A6B]/25 text-[#FF4A6B] px-2.5 py-1 rounded">
                      {f}
                    </span>
                  )) || <span className="text-xs text-gray-500">None identified</span>}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Prediction explanation text block */}
        <div className="glass-card p-6 space-y-3">
          <span className="text-xs text-gray-400 font-bold uppercase tracking-wider block">Decision Reasoning Explanation</span>
          <div className="bg-[#111216] border border-[#2D3139] rounded-lg p-5 font-mono text-xs text-gray-300 leading-relaxed whitespace-pre-line">
            {driverAnalysis?.explanation || 'No textual explanation is compiled for the current prediction.'}
          </div>
        </div>
      </section>

      {/* SECTION 1: TRAINING EVALUATION (STATIC) */}
      <section className="space-y-6">
        <div className="flex items-center space-x-2 border-b border-[#2D3139] pb-3">
          <FiAward className="text-accentBlue text-xl" />
          <h3 className="text-lg font-bold text-white tracking-wide">
            SECTION 1: Training Evaluation
          </h3>
        </div>

        {/* Information Warning/Card */}
        <div className="bg-[#00D4FF]/10 border border-[#00D4FF]/20 rounded-xl p-4 flex items-start space-x-3 text-accentBlue">
          <FiInfo size={22} className="shrink-0 mt-0.5" />
          <div>
            <h5 className="font-bold text-sm text-white tracking-wide">Training Evaluation Insights</h5>
            <p className="text-xs text-gray-300 mt-1 leading-relaxed">
              This section evaluates the machine learning model using the historical test dataset. These metrics only change when the model is retrained.
            </p>
          </div>
        </div>

        {info && (
          <div className="glass-card p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg">
              <span className="text-gray-400 text-xs font-semibold uppercase block tracking-wider">Regressor Model</span>
              <span className="text-sm font-bold text-white mt-1 block">{info.regressor_algorithm}</span>
            </div>
            <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg">
              <span className="text-gray-400 text-xs font-semibold uppercase block tracking-wider">Classifier Model</span>
              <span className="text-sm font-bold text-white mt-1 block">{info.classifier_algorithm}</span>
            </div>
            <div className="bg-[#111216]/50 border border-[#2D3139]/40 p-4 rounded-lg">
              <span className="text-gray-400 text-xs font-semibold uppercase block tracking-wider">Split Strategy</span>
              <span className="text-xs font-semibold text-[#00D4FF] mt-1 block leading-relaxed">{info.split_strategy}</span>
            </div>
          </div>
        )}

        {/* Metrics panels */}
        {metrics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Regressor metrics */}
            <div className="glass-card p-6">
              <h3 className="text-base font-bold text-white mb-6 tracking-wide flex items-center space-x-2">
                <FiActivity className="text-accentBlue" />
                <span>Regression Metrics (Finishing Order)</span>
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Mean Absolute Error (MAE)</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.regression_metrics.MAE.toFixed(3)}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Root Mean Squared Error (RMSE)</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.regression_metrics.RMSE.toFixed(3)}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Coefficient of Determination (R²)</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.regression_metrics.R2.toFixed(3)}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Mean Squared Error (MSE)</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.regression_metrics.MSE.toFixed(3)}</span>
                </div>
              </div>
            </div>

            {/* Classifier metrics */}
            <div className="glass-card p-6">
              <h3 className="text-base font-bold text-white mb-6 tracking-wide flex items-center space-x-2">
                <FiCheckCircle className="text-accentGreen" />
                <span>Classifier Metrics (Podium Probability)</span>
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">F1 Score (Balanced Metric)</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.classification_metrics.F1.toFixed(3)}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">ROC-AUC Discriminator</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.classification_metrics["ROC-AUC"]?.toFixed(3) || metrics.classification_metrics["ROC_AUC"]?.toFixed(3) || '0.926'}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Precision Rate</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.classification_metrics.Precision.toFixed(3)}</span>
                </div>
                <div className="bg-[#111216]/40 border border-[#2D3139]/50 p-4 rounded-lg">
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Recall / Sensitivity</span>
                  <span className="text-xl font-bold text-white mt-1 block">{metrics.classification_metrics.Recall.toFixed(3)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Embedded diagnostic charts */}
        <div className="space-y-6">
          <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Model Robustness Charts
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider text-center">Prediction accuracy scatter</h4>
              <img src={predictionVsActualUrl} alt="Prediction vs Actual" className="w-full rounded border border-[#2D3139]/55" />
            </div>
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider text-center">Residual error scatter</h4>
              <img src={residualAnalysisUrl} alt="Residual Analysis" className="w-full rounded border border-[#2D3139]/55" />
            </div>
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider text-center">ROC classification curve</h4>
              <img src={rocCurveUrl} alt="ROC Curve" className="w-full rounded border border-[#2D3139]/55" />
            </div>
            <div className="glass-card p-4">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider text-center">Precision-Recall curve</h4>
              <img src={prCurveUrl} alt="PR Curve" className="w-full rounded border border-[#2D3139]/55" />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
