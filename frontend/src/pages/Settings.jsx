import React, { useState, useEffect } from 'react';
import { healthApi } from '../services/api';
import { FiSettings, FiCheckCircle, FiAlertCircle, FiShield, FiSliders } from 'react-icons/fi';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Settings() {
  const [health, setHealth] = useState(null);
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    Promise.all([healthApi.checkHealth(), healthApi.checkVersion()])
      .then(([healthRes, versionRes]) => {
        setHealth(healthRes);
        setVersion(versionRes);
        setApiOnline(true);
        setLoading(false);
      })
      .catch(() => {
        setApiOnline(false);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-wide">System Settings</h2>
        <p className="text-gray-400 text-sm">Monitor backend server diagnostics, endpoints configurations, and security credentials.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* API Server status Card */}
        <div className="glass-card p-6 space-y-6">
          <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3 flex items-center space-x-2">
            <FiCheckCircle className="text-accentGreen" />
            <span>Server Connection Status</span>
          </h3>

          <div className="space-y-4">
            <div className="flex justify-between items-center bg-[#111216]/40 p-4 rounded border border-[#2D3139]/40">
              <span className="text-gray-400 text-sm">FastAPI Server status</span>
              <span className={`
                px-2.5 py-1 rounded text-xs font-bold flex items-center space-x-1.5
                ${apiOnline === true ? 'bg-accentGreen/15 text-accentGreen' : 'bg-accentRed/15 text-accentRed'}
              `}>
                <span className={`w-2 h-2 rounded-full ${apiOnline === true ? 'bg-accentGreen' : 'bg-accentRed'} animate-pulse`} />
                <span>{apiOnline === true ? 'ONLINE' : 'OFFLINE'}</span>
              </span>
            </div>

            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Endpoint Endpoint Cwd</span>
              <span className="text-white font-mono text-xs">{API_BASE_URL}</span>
            </div>

            {version && (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Software Version</span>
                  <span className="text-white font-semibold">{version.version}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">API Protocol Spec</span>
                  <span className="text-white font-semibold">{version.api_standard}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Deployment Author</span>
                  <span className="text-white font-semibold">{version.author}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Theme Card */}
        <div className="glass-card p-6 space-y-6">
          <h3 className="text-base font-bold text-white tracking-wide border-b border-[#2D3139] pb-3 flex items-center space-x-2">
            <FiSliders className="text-accentBlue" />
            <span>Theme Configuration</span>
          </h3>

          <div className="space-y-4">
            <p className="text-xs text-gray-400 leading-relaxed">
              Theme defaults to **Premium F1 Dark Theme** (Outfit typography, glassmorphic cards, HSL tailwind colors) 
              to provide maximum contrast for telemetry data models charts. Theme swapping is locked for portfolio standards.
            </p>

            <div className="flex justify-between items-center bg-[#111216]/40 p-4 rounded border border-[#2D3139]/40">
              <span className="text-gray-400 text-sm">Current Profile Theme</span>
              <span className="px-2.5 py-1 rounded text-xs font-bold bg-accentBlue/10 text-accentBlue">
                CARBON DARK
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
