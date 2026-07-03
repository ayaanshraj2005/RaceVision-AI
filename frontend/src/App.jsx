import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Drivers from './pages/Drivers';
import Teams from './pages/Teams';
import Circuits from './pages/Circuits';
import Predictions from './pages/Predictions';
import XAI from './pages/XAI';
import Models from './pages/Models';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="drivers" element={<Drivers />} />
          <Route path="teams" element={<Teams />} />
          <Route path="circuits" element={<Circuits />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="xai" element={<XAI />} />
          <Route path="models" element={<Models />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
