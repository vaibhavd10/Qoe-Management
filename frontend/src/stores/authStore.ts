import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'
import { User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  refreshToken: () => Promise<void>
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await authApi.login(email, password)
          const { access_token, user } = response
          
          // Store token in localStorage
          localStorage.setItem('token', access_token)
          
          set({ 
            user, 
            token: access_token, 
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('token')
        set({ user: null, token: null, isLoading: false })
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token')
        if (!token) {
          set({ user: null, token: null, isLoading: false })
          return
        }

        set({ isLoading: true })
        try {
          const user = await authApi.me()
          set({ user, token, isLoading: false })
        } catch (error) {
          // Token is invalid
          localStorage.removeItem('token')
          set({ user: null, token: null, isLoading: false })
        }
      },

      refreshToken: async () => {
        try {
          const response = await authApi.refreshToken()
          const { access_token } = response
          
          localStorage.setItem('token', access_token)
          set({ token: access_token })
        } catch (error) {
          get().logout()
          throw error
        }
      },

      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } })
        }
      }
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token 
      }),
    }
  )
)