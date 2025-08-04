import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'

interface SystemInfo {
  platform: string
  arch: string
  version: string
  electronVersion: string
  chromeVersion: string
  nodeVersion: string
}

interface SystemState {
  info: SystemInfo | null
  isLoading: boolean
  error: string | null
}

const initialState: SystemState = {
  info: null,
  isLoading: false,
  error: null
}

export const getSystemInfo = createAsyncThunk(
  'system/getInfo',
  async (_, { rejectWithValue }) => {
    try {
      const info = await window.electronAPI.system.getInfo()
      return info
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    setSystemInfo: (state, action: PayloadAction<SystemInfo>) => {
      state.info = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(getSystemInfo.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(getSystemInfo.fulfilled, (state, action) => {
        state.info = action.payload
        state.isLoading = false
      })
      .addCase(getSystemInfo.rejected, (state, action) => {
        state.error = action.payload as string
        state.isLoading = false
      })
  }
})

export const {
  setSystemInfo,
  setLoading,
  setError
} = systemSlice.actions

export default systemSlice.reducer 