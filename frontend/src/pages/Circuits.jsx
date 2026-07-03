import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../services/api';
import { FiMapPin, FiActivity, FiArrowRight } from 'react-icons/fi';

export default function Circuits() {
  const [circuits, setCircuits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    analyticsApi.getCircuits()
      .then((res) => {
        // Sort by total races
        const sorted = res.sort((a, b) => b.total_races - a.total_races);
        setCircuits(sorted);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch circuit telemetry.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="h-96 bg-[#181A20] animate-pulse rounded-xl border border-[#2D3139]" />;
  }

  if (error) {
    return <div className="glass-card p-6 text-accentRed">{error}</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-wide">Circuit Telemetry & Profiles</h2>
        <p className="text-gray-400 text-sm">Review track layouts and qualifying start-to-finish correlation indexes.</p>
      </div>

      {/* Monaco Alert banner */}
      <div className="bg-[#00D4FF]/10 border border-[#00D4FF]/30 rounded-xl p-6 flex items-start space-x-4">
        <div className="w-10 h-10 rounded bg-[#00D4FF]/20 text-[#00D4FF] flex items-center justify-center shrink-0">
          <FiActivity size={20} />
        </div>
        <div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-1">Qualifying Track Dominance</h4>
          <p className="text-xs text-gray-300 leading-relaxed">
            Tracks with high **Grid Importance Correlation (e.g. Monaco GP, correlation &gt; 0.50)** heavily favor qualifying pace. 
            Overtaking is mathematically limited, meaning starting grid positions dictate final positions. 
            On tracks with lower correlation (e.g. Spa, correlation &lt; 0.40), overtaking pace and strategy are much more critical.
          </p>
        </div>
      </div>

      {/* Table List */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#111216]/50 border-b border-[#2D3139]">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Circuit Name</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Location</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Country</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-center">Races Run</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400 text-right">Grid Correlation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2D3139]/40">
              {circuits.map((c) => (
                <tr key={c.circuit_id} className="hover:bg-white/5 transition-colors duration-150">
                  <td className="px-6 py-4 font-semibold text-white flex items-center space-x-2">
                    <FiMapPin className="text-[#00F29E]" size={14} />
                    <span>{c.circuit_name}</span>
                  </td>
                  <td className="px-6 py-4 text-gray-300">{c.location}</td>
                  <td className="px-6 py-4 text-gray-300">{c.country}</td>
                  <td className="px-6 py-4 text-gray-300 text-center font-bold">{c.total_races}</td>
                  <td className="px-6 py-4 text-right">
                    <span className={`
                      inline-block px-2.5 py-1 rounded text-xs font-bold
                      ${c.grid_importance_correlation >= 0.50 
                        ? 'bg-accentRed/10 text-accentRed' 
                        : c.grid_importance_correlation >= 0.40 
                          ? 'bg-accentYellow/10 text-accentYellow' 
                          : 'bg-accentGreen/10 text-accentGreen'
                      }
                    `}>
                      {c.grid_importance_correlation.toFixed(2)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
