import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FiUsers, FiAward, FiActivity, FiTrendingUp } from 'react-icons/fi';

const ACCENT_GREEN = '#00F29E';
const ACCENT_BLUE = '#00D4FF';
const ACCENT_YELLOW = '#FFC837';

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [teamData, setTeamData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingTeam, setLoadingTeam] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    analyticsApi.getTeams()
      .then((res) => {
        const sorted = res.sort((a, b) => a.constructor_name.localeCompare(b.constructor_name));
        setTeams(sorted);
        if (sorted.length > 0) {
          setSelectedTeamId(sorted[0].constructor_id);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch constructor data.');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (selectedTeamId) {
      setLoadingTeam(true);
      analyticsApi.getTeamById(selectedTeamId)
        .then((res) => {
          setTeamData(res);
          setLoadingTeam(false);
        })
        .catch((err) => {
          console.error(err);
          setLoadingTeam(false);
        });
    }
  }, [selectedTeamId]);

  if (loading) {
    return <div className="h-96 bg-[#181A20] animate-pulse rounded-xl border border-[#2D3139]" />;
  }

  if (error) {
    return <div className="glass-card p-6 text-accentRed">{error}</div>;
  }

  const chartData = teamData ? [
    { name: 'Races Started', Team: teamData.total_races, Average: 90 },
    { name: 'Podiums', Team: teamData.podiums, Average: 12 },
    { name: 'Wins', Team: teamData.wins, Average: 4 }
  ] : [];

  return (
    <div className="space-y-8">
      {/* Header Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide">Constructor Team Analytics</h2>
          <p className="text-gray-400 text-sm">Analyze car development indices and constructor telemetry patterns.</p>
        </div>
        <div className="w-full sm:w-64">
          <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Select Team</label>
          <select 
            className="w-full bg-[#181A20] border border-[#2D3139] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accentGreen"
            value={selectedTeamId}
            onChange={(e) => setSelectedTeamId(e.target.value)}
          >
            {teams.map((t) => (
              <option key={t.constructor_id} value={t.constructor_id}>{t.constructor_name}</option>
            ))}
          </select>
        </div>
      </div>

      {teamData && (
        <div className={`grid grid-cols-1 lg:grid-cols-3 gap-8 transition-opacity duration-300 ${loadingTeam ? 'opacity-50' : 'opacity-100'}`}>
          {/* Constructor card */}
          <div className="glass-card p-6 flex flex-col justify-between space-y-6 lg:col-span-1">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-accentBlue to-accentGreen flex items-center justify-center text-darkBg">
                <FiUsers size={32} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">{teamData.constructor_name}</h3>
                <span className="text-sm text-[#00D4FF] font-medium">{teamData.nationality}</span>
              </div>
            </div>

            <div className="border-t border-[#2D3139]/60 pt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Team Code ID</span>
                <span className="text-white font-semibold">C{teamData.constructor_id}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">HQ Nationality</span>
                <span className="text-white font-semibold">{teamData.nationality}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Historical Entries</span>
                <span className="text-white font-semibold">{teamData.total_races} entries</span>
              </div>
            </div>
          </div>

          {/* Stats details */}
          <div className="lg:col-span-2 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {/* Wins */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#FFC837]/10 text-accentYellow flex items-center justify-center">
                  <FiAward size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Wins</span>
                  <h4 className="text-2xl font-bold text-white mt-1">{teamData.wins}</h4>
                </div>
              </div>

              {/* Podiums */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#00F29E]/10 text-accentGreen flex items-center justify-center">
                  <FiTrendingUp size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Podiums</span>
                  <h4 className="text-2xl font-bold text-white mt-1">{teamData.podiums}</h4>
                </div>
              </div>

              {/* Podium Rate */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#00D4FF]/10 text-accentBlue flex items-center justify-center">
                  <FiActivity size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Podium Rate</span>
                  <h4 className="text-2xl font-bold text-white mt-1">
                    {teamData.total_races > 0 
                      ? `${((teamData.podiums / teamData.total_races) * 100).toFixed(1)}%`
                      : '0.0%'
                    }
                  </h4>
                </div>
              </div>
            </div>

            {/* Recharts chart */}
            <div className="glass-card p-6">
              <h3 className="text-base font-bold text-white mb-6 tracking-wide">
                Constructor Profile vs F1 Team Medians
              </h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2D3139" vertical={false} />
                    <XAxis dataKey="name" stroke="#A0A5B1" />
                    <YAxis stroke="#A0A5B1" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#181A20', borderColor: '#2D3139' }} 
                      labelStyle={{ color: 'white' }}
                    />
                    <Bar dataKey="Team" fill={ACCENT_BLUE} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Average" fill="#3D4251" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
