import React, { useState, useEffect } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  FiGrid, FiUser, FiUsers, FiMapPin, FiTrendingUp, 
  FiCpu, FiBarChart2, FiSettings, FiMenu, FiX, FiCheckCircle, FiAlertCircle 
} from 'react-icons/fi';
import { healthApi } from '../services/api';

const menuItems = [
  { path: '/', label: 'Dashboard', icon: FiGrid },
  { path: '/drivers', label: 'Driver Analytics', icon: FiUser },
  { path: '/teams', label: 'Team Analytics', icon: FiUsers },
  { path: '/circuits', label: 'Circuit Analytics', icon: FiMapPin },
  { path: '/predictions', label: 'AI Prediction Center', icon: FiTrendingUp },
  { path: '/xai', label: 'Explainable AI', icon: FiCpu },
  { path: '/models', label: 'Model Performance', icon: FiBarChart2 },
  { path: '/settings', label: 'Settings', icon: FiSettings },
];

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    const checkApiStatus = () => {
      healthApi.checkHealth()
        .then(() => setApiOnline(true))
        .catch(() => setApiOnline(false));
    };
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#111216] flex text-gray-200">
      {/* Mobile Sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Navigation */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-[#181A20] border-r border-[#2D3139] flex flex-col transform transition-transform duration-300 md:translate-x-0 md:static md:h-screen
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-16 flex items-center px-6 border-b border-[#2D3139] justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-[#00F29E] to-[#00D4FF] flex items-center justify-center text-[#111216] font-bold text-lg">
              RV
            </div>
            <span className="font-bold text-lg tracking-wide text-white bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text">
              RaceVision AI
            </span>
          </div>
          <button className="md:hidden text-gray-400 hover:text-white" onClick={() => setSidebarOpen(false)}>
            <FiX size={20} />
          </button>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                  ${isActive 
                    ? 'bg-gradient-to-r from-[#00F29E]/15 to-[#00D4FF]/5 text-[#00F29E] border-l-4 border-[#00F29E] pl-3' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5 border-l-4 border-transparent'}
                `}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-[#2D3139] text-xs text-gray-500 text-center">
          Portfolio Analytics v1.0
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Sticky Header */}
        <header className="h-16 bg-[#181A20]/80 backdrop-blur-md border-b border-[#2D3139] flex items-center justify-between px-6 z-30 shrink-0">
          <div className="flex items-center space-x-4">
            <button className="md:hidden text-gray-400 hover:text-white" onClick={() => setSidebarOpen(true)}>
              <FiMenu size={22} />
            </button>
            <h1 className="text-lg font-semibold text-white tracking-wide">
              Motorsport Analytics Suite
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            {/* Live API Health Check */}
            <div className={`
              flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-medium bg-[#111216]/50
              ${apiOnline === true ? 'border-[#00F29E]/30 text-[#00F29E]' : 'border-[#FF4A6B]/30 text-[#FF4A6B]'}
            `}>
              {apiOnline === true ? (
                <>
                  <FiCheckCircle className="animate-pulse" />
                  <span>API ONLINE</span>
                </>
              ) : (
                <>
                  <FiAlertCircle className="animate-pulse" />
                  <span>API OFFLINE</span>
                </>
              )}
            </div>
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-white">
              F1
            </div>
          </div>
        </header>

        {/* Scrollable Page Wrapper */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#111216]">
          <div className="max-w-7xl mx-auto space-y-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
