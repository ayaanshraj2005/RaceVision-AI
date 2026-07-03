import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error Interceptor:', error.response || error.message);
    const message = error.response?.data?.detail || error.response?.data?.message || 'Server connection failed.';
    return Promise.reject(new Error(message));
  }
);

export const predictionApi = {
  getFinishPosition: (payload) => api.post('/predict/finish-position', payload).then((res) => res.data),
  getPodiumProbability: (payload) => api.post('/predict/podium-probability', payload).then((res) => res.data),
  getDriverPerformance: (payload) => api.post('/predict/driver-performance', payload).then((res) => res.data),
  getTeamPerformance: (payload) => api.post('/predict/team-performance', payload).then((res) => res.data),
};

export const analyticsApi = {
  getDashboard: () => api.get('/analytics/dashboard').then((res) => res.data),
  getDrivers: () => api.get('/analytics/drivers').then((res) => res.data),
  getDriverById: (id) => api.get(`/analytics/drivers/${id}`).then((res) => res.data),
  getTeams: () => api.get('/analytics/teams').then((res) => res.data),
  getTeamById: (id) => api.get(`/analytics/teams/${id}`).then((res) => res.data),
  getCircuits: () => api.get('/analytics/circuits').then((res) => res.data),
  getSeasons: () => api.get('/analytics/seasons').then((res) => res.data),
};

export const explainApi = {
  getFeatureImportance: () => api.get('/explain/feature-importance').then((res) => res.data),
  explainPrediction: (payload) => api.post('/explain/prediction', payload).then((res) => res.data),
  getModelMetrics: () => api.get('/model/metrics').then((res) => res.data),
  getModelInfo: () => api.get('/model/information').then((res) => res.data),
  getDriversList: (season) => api.get('/drivers', { params: { season } }).then((res) => res.data),
  getDriverDetails: (driverName, season) => api.get(`/drivers/${encodeURIComponent(driverName)}`, { params: { season } }).then((res) => res.data),
};

export const healthApi = {
  checkHealth: () => api.get('/health').then((res) => res.data),
  checkVersion: () => api.get('/version').then((res) => res.data),
};

export default api;
