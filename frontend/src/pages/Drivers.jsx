import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FiUser, FiActivity, FiFlag, FiTrendingUp, FiAward } from 'react-icons/fi';

const ACCENT_GREEN = '#00F29E';
const ACCENT_BLUE = '#00D4FF';
const ACCENT_YELLOW = '#FFC837';

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [selectedDriverId, setSelectedDriverId] = useState('');
  const [driverData, setDriverData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDriver, setLoadingDriver] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    analyticsApi.getDrivers()
      .then((res) => {
        // Sort drivers alphabetically
        const sorted = res.sort((a, b) => a.driver_name.localeCompare(b.driver_name));
        setDrivers(sorted);
        if (sorted.length > 0) {
          // Pre-select first driver (e.g. Hamilton or similar)
          setSelectedDriverId(sorted[0].driver_id);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch driver stats.');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (selectedDriverId) {
      setLoadingDriver(true);
      analyticsApi.getDriverById(selectedDriverId)
        .then((res) => {
          setDriverData(res);
          setLoadingDriver(false);
        })
        .catch((err) => {
          console.error(err);
          setLoadingDriver(false);
        });
    }
  }, [selectedDriverId]);

  if (loading) {
    return <div className="h-96 bg-[#181A20] animate-pulse rounded-xl border border-[#2D3139]" />;
  }

  if (error) {
    return <div className="glass-card p-6 text-accentRed">{error}</div>;
  }

  // Prep chart data comparing driver to overall grid median
  const chartData = driverData ? [
    { name: 'Starts', Driver: driverData.total_races, Average: 45 },
    { name: 'Podiums', Driver: driverData.podiums, Average: 5 },
    { name: 'Wins', Driver: driverData.wins, Average: 2 }
  ] : [];

  return (
    <div className="space-y-8">
      {/* Header with Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide">Driver Career Analytics</h2>
          <p className="text-gray-400 text-sm">Compare drivers capabilities and historical F1 points distributions.</p>
        </div>
        <div className="w-full sm:w-64">
          <label className="text-xs text-gray-400 font-semibold uppercase block mb-1">Select Driver</label>
          <select 
            className="w-full bg-[#181A20] border border-[#2D3139] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accentGreen"
            value={selectedDriverId}
            onChange={(e) => setSelectedDriverId(e.target.value)}
          >
            {drivers.map((drv) => (
              <option key={drv.driver_id} value={drv.driver_id}>{drv.driver_name}</option>
            ))}
          </select>
        </div>
      </div>

      {driverData && (
        <div className={`grid grid-cols-1 lg:grid-cols-3 gap-8 transition-opacity duration-300 ${loadingDriver ? 'opacity-50' : 'opacity-100'}`}>
          {/* Profile Card */}
          <div className="glass-card p-6 flex flex-col justify-between space-y-6 lg:col-span-1">
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-accentGreen to-accentBlue flex items-center justify-center text-darkBg">
                <FiUser size={32} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">{driverData.driver_name}</h3>
                <span className="text-sm text-[#00D4FF] font-medium">{driverData.nationality}</span>
              </div>
            </div>

            <div className="border-t border-[#2D3139]/60 pt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Driver Code</span>
                <span className="text-white font-semibold">{driverData.code || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Date of Birth</span>
                <span className="text-white font-semibold">{driverData.dob}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Championship Entries</span>
                <span className="text-white font-semibold">{driverData.total_races} races</span>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="lg:col-span-2 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {/* Wins */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#FFC837]/10 text-accentYellow flex items-center justify-center">
                  <FiAward size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Wins</span>
                  <h4 className="text-2xl font-bold text-white mt-1">{driverData.wins}</h4>
                </div>
              </div>

              {/* Podiums */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#00F29E]/10 text-accentGreen flex items-center justify-center">
                  <FiTrendingUp size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Podiums</span>
                  <h4 className="text-2xl font-bold text-white mt-1">{driverData.podiums}</h4>
                </div>
              </div>

              {/* Win Rate */}
              <div className="bg-[#181A20]/50 border border-[#2D3139]/40 rounded-xl p-6 flex items-center space-x-4">
                <div className="w-10 h-10 rounded bg-[#00D4FF]/10 text-accentBlue flex items-center justify-center">
                  <FiActivity size={20} />
                </div>
                <div>
                  <span className="text-gray-400 text-xs font-semibold block uppercase">Win Rate</span>
                  <h4 className="text-2xl font-bold text-white mt-1">
                    {driverData.total_races > 0 
                      ? `${((driverData.wins / driverData.total_races) * 100).toFixed(1)}%`
                      : '0.0%'
                    }
                  </h4>
                </div>
              </div>
            </div>

            {/* Performance Comparison Chart */}
            <div className="glass-card p-6">
              <h3 className="text-base font-bold text-white mb-6 tracking-wide">
                Driver Profile Comparison vs Grid Median
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
                    <Bar dataKey="Driver" fill={ACCENT_GREEN} radius={[4, 4, 0, 0]} />
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
