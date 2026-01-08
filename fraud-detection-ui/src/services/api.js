import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://frauddetectionsystem-production.up.railway.app';
const API_KEY = process.env.REACT_APP_API_KEY || 'your-api-key';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

export const checkFraud = async (mode, transactionData) => {
  const response = await api.post('/api/check-fraud', {
    mode,
    ...transactionData
  });
  return response.data;
};

export const submitFeedback = async (predictionId, actualClass, note) => {
  const response = await api.post(`/api/predictions/${predictionId}/feedback`, {
    actual_class: actualClass,
    feedback_note: note
  });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/stats');
  return response.data;
};

export default api;