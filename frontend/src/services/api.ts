import axios, { AxiosResponse } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-store')
    if (token) {
      try {
        const authData = JSON.parse(token)
        if (authData.state.accessToken) {
          config.headers.Authorization = `Bearer ${authData.state.accessToken}`
        }
      } catch (error) {
        console.error('Error parsing auth token:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const authStore = localStorage.getItem('auth-store')
        if (authStore) {
          const authData = JSON.parse(authStore)
          const refreshToken = authData.state.refreshToken
          
          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken
            })
            
            const newToken = response.data.access_token
            authData.state.accessToken = newToken
            localStorage.setItem('auth-store', JSON.stringify(authData))
            
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        localStorage.removeItem('auth-store')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  getMe: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async () => {
    await api.post('/auth/logout')
  },
}

// Projects API
export const projectsApi = {
  getProjects: async (params?: any) => {
    const response = await api.get('/projects', { params })
    return response.data
  },

  getProject: async (id: number) => {
    const response = await api.get(`/projects/${id}`)
    return response.data
  },

  createProject: async (projectData: any) => {
    const response = await api.post('/projects', projectData)
    return response.data
  },

  updateProject: async (id: number, projectData: any) => {
    const response = await api.put(`/projects/${id}`, projectData)
    return response.data
  },

  deleteProject: async (id: number) => {
    const response = await api.delete(`/projects/${id}`)
    return response.data
  },

  getProjectDashboard: async (id: number) => {
    const response = await api.get(`/projects/${id}/dashboard`)
    return response.data
  },

  getDashboardOverview: async () => {
    const response = await api.get('/projects/dashboard/overview')
    return response.data
  },

  getRecentProjects: async (limit = 5) => {
    const response = await api.get('/projects/recent', { params: { limit } })
    return response.data
  },

  searchProjects: async (query: string) => {
    const response = await api.get('/projects/search', { params: { q: query } })
    return response.data
  },
}

// Documents API
export const documentsApi = {
  getDocuments: async (params?: any) => {
    const response = await api.get('/documents', { params })
    return response.data
  },

  getDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}`)
    return response.data
  },

  uploadDocument: async (file: File, projectId: number) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId.toString())
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  deleteDocument: async (id: number) => {
    const response = await api.delete(`/documents/${id}`)
    return response.data
  },

  getProcessingStatus: async (id: number) => {
    const response = await api.get(`/documents/${id}/status`)
    return response.data
  },
}

// Adjustments API
export const adjustmentsApi = {
  getAdjustments: async (params?: any) => {
    const response = await api.get('/adjustments', { params })
    return response.data
  },

  getAdjustment: async (id: number) => {
    const response = await api.get(`/adjustments/${id}`)
    return response.data
  },

  createAdjustment: async (adjustmentData: any) => {
    const response = await api.post('/adjustments', adjustmentData)
    return response.data
  },

  updateAdjustment: async (id: number, adjustmentData: any) => {
    const response = await api.put(`/adjustments/${id}`, adjustmentData)
    return response.data
  },

  reviewAdjustment: async (id: number, reviewData: any) => {
    const response = await api.post(`/adjustments/${id}/review`, reviewData)
    return response.data
  },

  bulkReviewAdjustments: async (adjustmentIds: number[], action: string) => {
    const response = await api.post('/adjustments/bulk-review', {
      adjustment_ids: adjustmentIds,
      action,
    })
    return response.data
  },
}

// Questions API
export const questionsApi = {
  getQuestions: async (params?: any) => {
    const response = await api.get('/questions', { params })
    return response.data
  },

  getQuestion: async (id: number) => {
    const response = await api.get(`/questions/${id}`)
    return response.data
  },

  createQuestion: async (questionData: any) => {
    const response = await api.post('/questions', questionData)
    return response.data
  },

  updateQuestion: async (id: number, questionData: any) => {
    const response = await api.put(`/questions/${id}`, questionData)
    return response.data
  },

  answerQuestion: async (id: number, answerData: any) => {
    const response = await api.post(`/questions/${id}/answer`, answerData)
    return response.data
  },

  generateQuestionnaire: async (projectId: number, config: any) => {
    const response = await api.post('/questions/generate', { project_id: projectId, ...config })
    return response.data
  },
}

// Reports API
export const reportsApi = {
  getReports: async (params?: any) => {
    const response = await api.get('/reports', { params })
    return response.data
  },

  getReport: async (id: number) => {
    const response = await api.get(`/reports/${id}`)
    return response.data
  },

  generateReport: async (reportData: any) => {
    const response = await api.post('/reports/generate', reportData)
    return response.data
  },

  downloadReport: async (id: number) => {
    const response = await api.get(`/reports/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  updateReportQA: async (id: number, qaData: any) => {
    const response = await api.put(`/reports/${id}/qa`, qaData)
    return response.data
  },
}

export default api