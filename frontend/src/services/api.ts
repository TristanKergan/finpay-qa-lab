const API_BASE = '/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const api = {
  getToken: () => localStorage.getItem('finpay_access_token'),
  setTokens: (access: string, refresh: string) => {
    localStorage.setItem('finpay_access_token', access);
    localStorage.setItem('finpay_refresh_token', refresh);
  },
  clearTokens: () => {
    localStorage.removeItem('finpay_access_token');
    localStorage.removeItem('finpay_refresh_token');
    localStorage.removeItem('finpay_user');
  },

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = api.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 204) {
      return {} as T;
    }

    const contentType = res.headers.get('content-type');
    let data: any = null;
    if (contentType && contentType.includes('application/json')) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const detail = typeof data === 'object' && data?.detail ? data.detail : 'Request failed';
      throw new ApiError(res.status, detail, data);
    }

    return data as T;
  },

  // Auth
  register: (body: any) => api.request<any>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body: any) => api.request<any>('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  refresh: (refresh_token: string) => api.request<any>('/auth/refresh', { method: 'POST', body: JSON.stringify({ refresh_token }) }),
  logout: (refresh_token: string) => api.request<void>('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token }) }),
  changePassword: (body: any) => api.request<any>('/auth/password/change', { method: 'POST', body: JSON.stringify(body) }),

  // User
  getMe: () => api.request<any>('/users/me'),
  updateProfile: (body: any) => api.request<any>('/users/me', { method: 'PATCH', body: JSON.stringify(body) }),
  getUsers: () => api.request<any[]>('/users'),

  // Wallet
  getWallet: () => api.request<any>('/wallet'),

  // Transfers
  createTransfer: (body: any) => api.request<any>('/transfers', { method: 'POST', body: JSON.stringify(body) }),
  getTransfer: (id: string) => api.request<any>(`/transfers/${id}`),

  // Transactions
  getTransactions: (params: Record<string, string | number> = {}) => {
    const query = new URLSearchParams(params as any).toString();
    return api.request<any>(`/transactions?${query}`);
  },
  getTransaction: (id: string) => api.request<any>(`/transactions/${id}`),

  // Cards
  getCards: () => api.request<any[]>('/cards'),
  createCard: (body: any) => api.request<any>('/cards', { method: 'POST', body: JSON.stringify(body) }),
  freezeCard: (id: string) => api.request<any>(`/cards/${id}/freeze`, { method: 'PATCH' }),
  unfreezeCard: (id: string) => api.request<any>(`/cards/${id}/unfreeze`, { method: 'PATCH' }),
  deleteCard: (id: string) => api.request<void>(`/cards/${id}`, { method: 'DELETE' }),

  // Notifications
  getNotifications: () => api.request<any>('/notifications'),
  markNotificationRead: (id: string) => api.request<any>(`/notifications/${id}/read`, { method: 'PATCH' }),
  markAllNotificationsRead: () => api.request<any>('/notifications/read-all', { method: 'POST' }),
};
