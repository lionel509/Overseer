import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'

interface PythonState {
  isRunning: boolean
  isConnected: boolean
  output: string[]
  error: string | null
  lastCommand: string | null
  lastResponse: any | null
}

const initialState: PythonState = {
  isRunning: false,
  isConnected: false,
  output: [],
  error: null,
  lastCommand: null,
  lastResponse: null
}

// Async thunks for Python operations
export const startPythonBackend = createAsyncThunk(
  'python/start',
  async (_, { rejectWithValue }) => {
    try {
      const result = await window.electronAPI.python.start()
      if (!result) {
        throw new Error('Failed to start Python backend')
      }
      return result
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

export const stopPythonBackend = createAsyncThunk(
  'python/stop',
  async (_, { rejectWithValue }) => {
    try {
      const result = await window.electronAPI.python.stop()
      return result
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

export const executePythonCommand = createAsyncThunk(
  'python/execute',
  async ({ command, args }: { command: string; args?: any[] }, { rejectWithValue }) => {
    try {
      const result = await window.electronAPI.python.execute(command, args || [])
      return result
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error')
    }
  }
)

const pythonSlice = createSlice({
  name: 'python',
  initialState,
  reducers: {
    setRunning: (state, action: PayloadAction<boolean>) => {
      state.isRunning = action.payload
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload
    },
    addOutput: (state, action: PayloadAction<string>) => {
      state.output.push(action.payload)
      // Keep only last 1000 lines
      if (state.output.length > 1000) {
        state.output = state.output.slice(-1000)
      }
    },
    clearOutput: (state) => {
      state.output = []
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    setLastCommand: (state, action: PayloadAction<string>) => {
      state.lastCommand = action.payload
    },
    setLastResponse: (state, action: PayloadAction<any>) => {
      state.lastResponse = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(startPythonBackend.pending, (state) => {
        state.isRunning = false
        state.error = null
      })
      .addCase(startPythonBackend.fulfilled, (state) => {
        state.isRunning = true
        state.isConnected = true
        state.error = null
      })
      .addCase(startPythonBackend.rejected, (state, action) => {
        state.isRunning = false
        state.isConnected = false
        state.error = action.payload as string
      })
      .addCase(stopPythonBackend.fulfilled, (state) => {
        state.isRunning = false
        state.isConnected = false
      })
      .addCase(executePythonCommand.pending, (state, action) => {
        state.lastCommand = action.meta.arg.command
        state.error = null
      })
      .addCase(executePythonCommand.fulfilled, (state, action) => {
        state.lastResponse = action.payload
        if (!action.payload.success) {
          state.error = action.payload.error
        }
      })
      .addCase(executePythonCommand.rejected, (state, action) => {
        state.error = action.payload as string
      })
  }
})

export const {
  setRunning,
  setConnected,
  addOutput,
  clearOutput,
  setError,
  setLastCommand,
  setLastResponse
} = pythonSlice.actions

export default pythonSlice.reducer 