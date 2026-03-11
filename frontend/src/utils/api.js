import axios from 'axios';

// In dev, call backend directly to avoid flaky CRA proxy behavior on some POST requests.
// In production, default to same-origin /api unless REACT_APP_BACKEND_URL is provided.
const isDevOrigin =
  typeof window !== 'undefined' &&
  ['localhost', '127.0.0.1'].includes(window.location?.hostname) &&
  (window.location?.port === '3000' || window.location?.port === '');
const DEFAULT_DEV_BACKEND = 'http://127.0.0.1:8000';
const configuredBackend = (process.env.REACT_APP_BACKEND_URL || '').trim();
const BACKEND_URL = configuredBackend || (isDevOrigin ? DEFAULT_DEV_BACKEND : '');
const API_BASE = BACKEND_URL ? BACKEND_URL.replace(/\/api\/?$/, '') + '/api' : '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors: don't redirect for auth endpoints (login/register/google) so user sees error message
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url ?? '';
    const isAuthEndpoint = /\/auth\/(me|login|register|google|send-signup-otp|verify-signup-otp)/.test(url);

    if (url.includes('/auth/me')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return Promise.reject(error);
    }
    // On 401, only clear and redirect for protected routes — not for login/register so toast shows
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
export { API_BASE };
