import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('voice_ai_api_key');
    if (apiKey) {
      config.headers['x-api-key'] = apiKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('voice_ai_api_key');
      localStorage.removeItem('voice_ai_username');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Health check
  health: () => api.get('/health'),
  
  // Authentication
  login: (username, apiKey) => api.post('/api/auth/login', { username, api_key: apiKey }),
  
  // Chat endpoints
  chat: (message) => api.post('/chat', { message }),
  transcribe: (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    return api.post('/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Phase 5B endpoints
  multiparty: {
    createSession: (sessionData) => api.post('/api/v2/sessions/multiparty', sessionData),
    joinSession: (sessionId, speakerData) => api.post(`/api/v2/sessions/multiparty/${sessionId}/join`, speakerData),
    getSpeakers: (sessionId) => api.get(`/api/v2/sessions/multiparty/${sessionId}/speakers`),
    leaveSession: (sessionId) => api.delete(`/api/v2/sessions/multiparty/${sessionId}/leave`),
  },
  
  memory: {
    getSummary: (sessionId) => api.get(`/api/v2/memory/summary/${sessionId}`),
    retainSession: (sessionId) => api.post(`/api/v2/memory/retain/${sessionId}`),
    getUserSessions: (userId) => api.get(`/api/v2/memory/sessions/${userId}`),
  },
  
  localMode: {
    toggle: () => api.post('/api/v2/local-mode/toggle'),
    getStatus: () => api.get('/api/v2/local-mode/status'),
    getCapabilities: () => api.get('/api/v2/local-mode/capabilities'),
  },
  
  // Session management
  sessions: {
    list: () => api.get('/v4/sessions'),
    create: (sessionData) => api.post('/v4/sessions', sessionData),
    get: (sessionId) => api.get(`/v4/sessions/${sessionId}`),
    history: (sessionId) => api.get(`/v4/session/${sessionId}/history`),
  },
};
