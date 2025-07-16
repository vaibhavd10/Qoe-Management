import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token')
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },
  
  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
  
  me: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
  
  refreshToken: async () => {
    const response = await api.post('/auth/refresh')
    return response.data
  },
  
  logout: async () => {
    await api.post('/auth/logout')
  }
}

// Projects API
export const projectsApi = {
  getProjects: async () => {
    const response = await api.get('/projects')
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
    await api.delete(`/projects/${id}`)
  },
  
  getDashboardOverview: async () => {
    const response = await api.get('/projects/dashboard/overview')
    return response.data
  },
  
  getRecentProjects: async (limit: number = 5) => {
    const response = await api.get(`/projects/recent?limit=${limit}`)
    return response.data
  }
}

// Documents API
export const documentsApi = {
  getDocuments: async (projectId?: number | null) => {
    const params = projectId ? { project_id: projectId } : {}
    const response = await api.get('/documents', { params })
    return response.data
  },
  
  getDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}`)
    return response.data
  },
  
  uploadDocument: async (formData: FormData) => {
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  deleteDocument: async (id: number) => {
    await api.delete(`/documents/${id}`)
  },
  
  downloadDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },
  
  processDocument: async (id: number) => {
    const response = await api.post(`/documents/${id}/process`)
    return response.data
  }
}

// Adjustments API
export const adjustmentsApi = {
  getAdjustments: async (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {}
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
  
  reviewAdjustment: async (data: any) => {
    const response = await api.post(`/adjustments/${data.id}/review`, data)
    return response.data
  },
  
  deleteAdjustment: async (id: number) => {
    await api.delete(`/adjustments/${id}`)
  }
}

// Questions API
export const questionsApi = {
  getQuestions: async (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {}
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
  
  answerQuestion: async (data: any) => {
    const response = await api.post(`/questions/${data.questionId}/answer`, data)
    return response.data
  },
  
  deleteQuestion: async (id: number) => {
    await api.delete(`/questions/${id}`)
  }
}

// Reports API
export const reportsApi = {
  getReports: async (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {}
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
  
  deleteReport: async (id: number) => {
    await api.delete(`/reports/${id}`)
  }
}

// Users API
export const usersApi = {
  getUsers: async () => {
    const response = await api.get('/users')
    return response.data
  },
  
  getUser: async (id: number) => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },
  
  createUser: async (userData: any) => {
    const response = await api.post('/users', userData)
    return response.data
  },
  
  updateUser: async (id: number, userData: any) => {
    const response = await api.put(`/users/${id}`, userData)
    return response.data
  },
  
  updateProfile: async (profileData: any) => {
    const response = await api.put('/users/profile', profileData)
    return response.data
  },
  
  changePassword: async (passwordData: any) => {
    const response = await api.put('/users/password', passwordData)
    return response.data
  },
  
  deleteUser: async (id: number) => {
    await api.delete(`/users/${id}`)
  }
}

export default api