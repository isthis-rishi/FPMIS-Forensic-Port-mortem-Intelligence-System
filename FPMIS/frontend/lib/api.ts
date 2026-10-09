import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (email: string, password: string) => {
    const res = await api.post('/api/auth/login', { email, password });
    return res.data;
  },
  register: async (data: any) => {
    const res = await api.post('/api/auth/register', data);
    return res.data;
  },
  me: async () => {
    const res = await api.get('/api/auth/me');
    return res.data;
  },
  changePassword: async (current_password: string, new_password: string) => {
    const res = await api.post('/api/auth/change-password', { current_password, new_password });
    return res.data;
  },
};

export const casesApi = {
  list: async (params?: { page?: number; status?: string; search?: string }) => {
    const res = await api.get('/api/cases', { params });
    return res.data;
  },
  get: async (id: string) => {
    const res = await api.get(`/api/cases/${id}`);
    return res.data;
  },
  create: async (data: any) => {
    const res = await api.post('/api/cases', data);
    return res.data;
  },
  update: async (id: string, data: any) => {
    const res = await api.put(`/api/cases/${id}`, data);
    return res.data;
  },
  delete: async (id: string) => {
    const res = await api.delete(`/api/cases/${id}`);
    return res.data;
  },
  createDeceased: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/deceased`, data);
    return res.data;
  },
  updateDeceased: async (caseId: string, data: any) => {
    const res = await api.put(`/api/cases/${caseId}/deceased`, data);
    return res.data;
  },
  getAutopsy: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/autopsy`);
    return res.data;
  },
  createAutopsy: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/autopsy`, data);
    return res.data;
  },
  updateAutopsy: async (caseId: string, data: any) => {
    const res = await api.put(`/api/cases/${caseId}/autopsy`, data);
    return res.data;
  },
  finalizeAutopsy: async (caseId: string) => {
    const res = await api.post(`/api/cases/${caseId}/autopsy/finalize`);
    return res.data;
  },
  getInjuries: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/injuries`);
    return res.data;
  },
  addInjury: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/injuries`, data);
    return res.data;
  },
  deleteInjury: async (caseId: string, injuryId: string) => {
    const res = await api.delete(`/api/cases/${caseId}/injuries/${injuryId}`);
    return res.data;
  },
};

export const evidenceApi = {
  list: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/evidence`);
    return res.data;
  },
  get: async (evidenceId: string) => {
    const res = await api.get(`/api/evidence/${evidenceId}`);
    return res.data;
  },
  create: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/evidence`, data);
    return res.data;
  },
  update: async (evidenceId: string, data: any) => {
    const res = await api.put(`/api/evidence/${evidenceId}`, data);
    return res.data;
  },
  transfer: async (evidenceId: string, data: any) => {
    const res = await api.post(`/api/evidence/${evidenceId}/transfer`, data);
    return res.data;
  },
  sendToLab: async (evidenceId: string, labName: string, analysisType: string) => {
    const res = await api.post(`/api/evidence/${evidenceId}/send-to-lab`, null, {
      params: { lab_name: labName, analysis_type: analysisType },
    });
    return res.data;
  },
  getChain: async (evidenceId: string) => {
    const res = await api.get(`/api/evidence/${evidenceId}/chain`);
    return res.data;
  },
  getMyEvidence: async () => {
    const res = await api.get('/api/my-evidence');
    return res.data;
  },
};

export const todApi = {
  get: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/tod`);
    return res.data;
  },
  calculate: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/tod`, data);
    return res.data;
  },
  update: async (caseId: string, data: any) => {
    const res = await api.put(`/api/cases/${caseId}/tod`, data);
    return res.data;
  },
  adjust: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/tod/adjust`, data);
    return res.data;
  },
};

export const decompositionApi = {
  list: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/decomposition`);
    return res.data;
  },
  getLatest: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/decomposition/latest`);
    return res.data;
  },
  getStages: async (caseId?: string) => {
    const id = caseId || '00000000-0000-0000-0000-000000000000';
    const res = await api.get(`/api/cases/${id}/decomposition/stages`);
    return res.data;
  },
  log: async (caseId: string, data: any) => {
    const res = await api.post(`/api/cases/${caseId}/decomposition`, data);
    return res.data;
  },
};

export const missingPersonsApi = {
  list: async (params?: { status?: string; search?: string }) => {
    const res = await api.get('/api/missing-persons', { params });
    return res.data;
  },
  get: async (id: string) => {
    const res = await api.get(`/api/missing-persons/${id}`);
    return res.data;
  },
  create: async (data: any) => {
    const res = await api.post('/api/missing-persons', data);
    return res.data;
  },
  findMatches: async (caseId: string, minScore = 30) => {
    const res = await api.post(`/api/cases/${caseId}/find-matches`, null, {
      params: { min_score: minScore },
    });
    return res.data;
  },
  getMatches: async (caseId: string) => {
    const res = await api.get(`/api/cases/${caseId}/matches`);
    return res.data;
  },
  confirmMatch: async (matchId: string, data: any) => {
    const res = await api.post(`/api/matches/${matchId}/confirm`, data);
    return res.data;
  },
  rejectMatch: async (matchId: string, reason?: string) => {
    const res = await api.post(`/api/matches/${matchId}/reject`, null, {
      params: { reason },
    });
    return res.data;
  },
};

export const alertsApi = {
  list: async (params?: { status?: string; severity?: string }) => {
    const res = await api.get('/api/alerts', { params });
    return res.data;
  },
  get: async (id: string) => {
    const res = await api.get(`/api/alerts/${id}`);
    return res.data;
  },
  getStats: async () => {
    const res = await api.get('/api/alerts/stats');
    return res.data;
  },
  detect: async () => {
    const res = await api.post('/api/alerts/detect');
    return res.data;
  },
  updateStatus: async (id: string, status: string, notes?: string) => {
    const res = await api.put(`/api/alerts/${id}/status`, null, {
      params: { new_status: status, notes },
    });
    return res.data;
  },
  getRules: async () => {
    const res = await api.get('/api/alerts/rules');
    return res.data;
  },
};

export const searchApi = {
  search: async (filters: any, page = 1, pageSize = 20) => {
    const res = await api.post('/api/search', filters, {
      params: { page, page_size: pageSize },
    });
    return res.data;
  },
  quickSearch: async (query: string) => {
    const res = await api.get('/api/search/quick', { params: { q: query } });
    return res.data;
  },
  getStats: async () => {
    const res = await api.get('/api/search/stats');
    return res.data;
  },
  getUnidentified: async (params?: { days?: number; district?: string }) => {
    const res = await api.get('/api/search/unidentified', { params });
    return res.data;
  },
};

export default api;
