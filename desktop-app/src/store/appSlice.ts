import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface AppState {
  isInitialized: boolean
  isLoading: boolean
  error: string | null
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
}

const initialState: AppState = {
  isInitialized: false,
  isLoading: false,
  error: null,
  theme: 'light',
  sidebarCollapsed: false
}

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    initializeApp: (state) => {
      state.isLoading = true
    },
    initializeAppSuccess: (state) => {
      state.isInitialized = true
      state.isLoading = false
    },
    initializeAppFailure: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.isLoading = false
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload
    },
    clearError: (state) => {
      state.error = null
    }
  }
})

export const {
  initializeApp,
  initializeAppSuccess,
  initializeAppFailure,
  setTheme,
  toggleSidebar,
  setSidebarCollapsed,
  clearError
} = appSlice.actions

export default appSlice.reducer 