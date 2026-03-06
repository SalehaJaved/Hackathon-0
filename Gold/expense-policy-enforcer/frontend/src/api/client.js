import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const expensesApi = {
  // Submit expense with receipt
  submit: async (formData) => {
    const response = await api.post('/expenses/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // List expenses
  list: async (status = null) => {
    const params = status ? { status } : {};
    const response = await api.get('/expenses/', { params });
    return response.data;
  },

  // Get single expense
  get: async (id) => {
    const response = await api.get(`/expenses/${id}`);
    return response.data;
  },

  // Approve expense
  approve: async (id, reason = null) => {
    const response = await api.post(`/expenses/${id}/approve`, { reason });
    return response.data;
  },

  // Reject expense
  reject: async (id, reason = null) => {
    const response = await api.post(`/expenses/${id}/reject`, { reason });
    return response.data;
  },

  // Get dashboard stats
  getStats: async () => {
    const response = await api.get('/expenses/dashboard/stats');
    return response.data;
  },
};

export const policiesApi = {
  // List policies
  list: async (activeOnly = false) => {
    const params = activeOnly ? { active_only: true } : {};
    const response = await api.get('/policies/', { params });
    return response.data;
  },

  // Create policy
  create: async (policy) => {
    const response = await api.post('/policies/', policy);
    return response.data;
  },

  // Toggle policy
  toggle: async (id) => {
    const response = await api.patch(`/policies/${id}/toggle`);
    return response.data;
  },
};

export const auditApi = {
  // List audit logs
  list: async (expenseId = null) => {
    const params = expenseId ? { expense_id: expenseId } : {};
    const response = await api.get('/audit/', { params });
    return response.data;
  },
};

export default api;
