import { configureStore } from '@reduxjs/toolkit'
import appReducer from './appSlice'
import pythonReducer from './pythonSlice'
import commandPaletteReducer from './commandPaletteSlice'
import systemReducer from './systemSlice'

export const store = configureStore({
  reducer: {
    app: appReducer,
    python: pythonReducer,
    commandPalette: commandPaletteReducer,
    system: systemReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['python/output', 'python/error'],
        ignoredPaths: ['python.output', 'python.error']
      }
    })
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch 