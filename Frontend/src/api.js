import axios from "axios";

// Use environment variable for API base URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Session storage key
const SESSION_KEY = 'session_id';

// Get session ID from localStorage
export const getSessionId = () => localStorage.getItem(SESSION_KEY);

// Save session ID to localStorage
export const setSessionId = (sessionId) => {
  if (sessionId) {
    localStorage.setItem(SESSION_KEY, sessionId);
  }
};

// Clear session ID from localStorage
export const clearSessionId = () => localStorage.removeItem(SESSION_KEY);

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Add Authorization header with session ID to all requests
api.interceptors.request.use((config) => {
  const sessionId = getSessionId();
  if (sessionId) {
    config.headers.Authorization = `Bearer ${sessionId}`;
  }
  return config;
});

export default api;