import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email); 
    params.append('password', password);
    return api.post('/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  register: (userData) => api.post('/register', userData),
};

export const financeAPI = {
  getSummary: () => api.get('/analytics/summary'),
  getCategories: () => api.get('/analytics/category'),
  getTransactions: () => api.get('/transactions/'),
  uploadReceipt: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/transactions/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  saveTransaction: (data) => api.post('/transactions/', data),
};

export default api;