import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'analyst'
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  refreshAccessToken: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await authApi.login(email, password)
          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isLoading: false,
        })
      },

      checkAuth: async () => {
        const { accessToken, refreshToken } = get()
        if (!accessToken || !refreshToken) {
          return
        }

        try {
          const user = await authApi.getMe()
          set({ user })
        } catch (error) {
          // If getting user fails, try to refresh token
          try {
            await get().refreshAccessToken()
            const user = await authApi.getMe()
            set({ user })
          } catch (refreshError) {
            get().logout()
          }
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await authApi.refreshToken(refreshToken)
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
          })
        } catch (error) {
          get().logout()
          throw error
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)