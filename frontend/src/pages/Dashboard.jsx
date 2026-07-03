import React, { useState, useEffect } from 'react';
import { analyticsApi, explainApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { FiUsers, FiAward, FiMapPin, FiCalendar, FiFlag, FiTrendingUp } from 'react-icons/fi';

const ACCENT_GREEN = '#00F29E';
const ACCENT_BLUE = '#00D4FF';
const ACCENT_RED = '#FF4A6B';
const ACCENT_YELLOW = '#FFC837';
const ACCENT_PURPLE = '#D946EF';

const COLORS = [ACCENT_GREEN, ACCENT_BLUE, ACCENT_YELLOW, ACCENT_PURPLE, ACCENT_RED];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [featImportance, setFeatImportance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([analyticsApi.getDashboard(), explainApi.getFeatureImportance()])
      .then(([dashRes, explainRes]) => {
        setData(dashRes);
        // Format feature importance to list of { name, value }
        const formatted = Object.entries(explainRes.feature_importance)
          .map(([name, val]) => ({ name: name.replace(/_/g, ' '), value: parseFloat((val * 100).toFixed(2)) }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 8); // top 8 features
        setFeatImportance(formatted);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to connect to backend services.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        {/* KPI Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-[#181A20] border border-[#2D3139] rounded-xl" />
          ))}
        </div>
        {/* Charts Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="h-96 bg-[#181A20] border border-[#2D3139] rounded-xl" />
          <div className="h-96 bg-[#181A20] border border-[#2D3139] rounded-xl" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 text-center space-y-4">
        <FiAward className="mx-auto text-4xl text-accentRed" />
        <h3 className="text-xl font-bold text-white">System Error</h3>
        <p className="text-gray-400">{error}</p>
        <button 
          className="px-6 py-2 bg-gradient-to-r from-accentGreen to-accentBlue text-darkBg font-semibold rounded-lg hover:opacity-90"
          onClick={() => window.location.reload()}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const kpis = [
    { label: 'Total Drivers', value: data.total_drivers, icon: FiUsers, color: ACCENT_GREEN },
    { label: 'Total Constructors', value: data.total_constructors, icon: FiAward, color: ACCENT_BLUE },
    { label: 'Total Circuits', value: data.total_circuits, icon: FiMapPin, color: ACCENT_YELLOW },
    { label: 'Total Races Covered', value: data.total_races, icon: FiFlag, color: ACCENT_PURPLE },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-wide">RaceVision Overview</h2>
        <p className="text-gray-400 text-sm">F1 telemetry insights and performance predictions models diagnostics.</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="glass-card p-6 flex items-center space-x-4">
              <div 
                className="w-12 h-12 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${kpi.color}15`, color: kpi.color }}
              >
                <Icon size={24} />
              </div>
              <div>
                <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">{kpi.label}</span>
                <h4 className="text-2xl font-bold text-white mt-1">{kpi.value}</h4>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Driver wins chart */}
        <div className="glass-card p-6 flex flex-col">
          <h3 className="text-base font-bold text-white mb-6 tracking-wide flex items-center space-x-2">
            <span>Top Drivers by F1 GP Wins</span>
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_drivers_by_wins} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2D3139" horizontal={false} />
                <XAxis type="number" stroke="#A0A5B1" />
                <YAxis dataKey="driver_name" type="category" stroke="#A0A5B1" width={100} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#181A20', borderColor: '#2D3139' }} 
                  labelStyle={{ color: 'white' }}
                />
                <Bar dataKey="wins" fill={ACCENT_BLUE} radius={[0, 4, 4, 0]}>
                  {data.top_drivers_by_wins.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global ML Feature Importance chart */}
        <div className="glass-card p-6 flex flex-col">
          <h3 className="text-base font-bold text-white mb-6 tracking-wide flex items-center space-x-2">
            <span>Global Machine Learning Feature Importance</span>
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featImportance} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2D3139" horizontal={false} />
                <XAxis type="number" stroke="#A0A5B1" />
                <YAxis dataKey="name" type="category" stroke="#A0A5B1" width={120} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#181A20', borderColor: '#2D3139' }} 
                  labelStyle={{ color: 'white' }}
                />
                <Bar dataKey="value" fill={ACCENT_GREEN} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Constructor Wins Standings */}
      <div className="glass-card p-6">
        <h3 className="text-base font-bold text-white mb-6 tracking-wide">
          Championship Constructor Dominance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {data.top_teams_by_wins.map((team, idx) => (
            <div key={idx} className="bg-[#111216]/50 border border-[#2D3139]/40 rounded-lg p-4 flex flex-col items-center">
              <span className="text-xs text-gray-500 font-semibold mb-1 uppercase">P{idx+1}</span>
              <span className="text-sm font-bold text-white text-center line-clamp-1">{team.constructor_name}</span>
              <span className="text-xl font-extrabold text-[#00D4FF] mt-2">{team.wins} Wins</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
