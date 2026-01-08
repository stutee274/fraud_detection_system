import axios from 'axios';

// Use environment variable (set in Vercel)
const API_URL = process.env.REACT_APP_API_URL;
const API_KEY = process.env.REACT_APP_API_KEY;

console.log('API Config:', { API_URL, hasKey: !!API_KEY });

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY  // Match what backend expects
  },
  withCredentials: true  // Important for CORS
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const checkFraud = async (mode, transactionData) => {
  try {
    const response = await api.post('/api/check-fraud', {
      mode,
      ...transactionData
    });
    return response.data;
  } catch (error) {
    console.error('checkFraud error:', error);
    throw error;
  }
};

export const submitFeedback = async (predictionId, actualClass, note) => {
  try {
    const response = await api.post(`/api/predictions/${predictionId}/feedback`, {
      actual_class: actualClass,
      feedback_note: note || ''
    });
    return response.data;
  } catch (error) {
    console.error('submitFeedback error:', error);
    throw error;
  }
};

export const getStats = async () => {
  try {
    const response = await api.get('/api/stats');
    return response.data;
  } catch (error) {
    console.error('getStats error:', error);
    throw error;
  }
};

export default api;