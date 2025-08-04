import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Command {
  id: string
  title: string
  description: string
  category: string
  keywords: string[]
  action: () => void | Promise<void>
  shortcut?: string
  icon?: string
}

interface CommandPaletteState {
  isOpen: boolean
  searchQuery: string
  selectedIndex: number
  commands: Command[]
  filteredCommands: Command[]
  categories: string[]
  recentCommands: string[]
}

const initialState: CommandPaletteState = {
  isOpen: false,
  searchQuery: '',
  selectedIndex: 0,
  commands: [],
  filteredCommands: [],
  categories: [],
  recentCommands: []
}

const commandPaletteSlice = createSlice({
  name: 'commandPalette',
  initialState,
  reducers: {
    openCommandPalette: (state) => {
      state.isOpen = true
      state.selectedIndex = 0
    },
    closeCommandPalette: (state) => {
      state.isOpen = false
      state.searchQuery = ''
      state.selectedIndex = 0
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload
      state.selectedIndex = 0
      // Filter commands based on search query
      const query = action.payload.toLowerCase()
      state.filteredCommands = state.commands.filter(command => 
        command.title.toLowerCase().includes(query) ||
        command.description.toLowerCase().includes(query) ||
        command.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
        command.category.toLowerCase().includes(query)
      )
    },
    selectNext: (state) => {
      if (state.selectedIndex < state.filteredCommands.length - 1) {
        state.selectedIndex++
      }
    },
    selectPrevious: (state) => {
      if (state.selectedIndex > 0) {
        state.selectedIndex--
      }
    },
    selectCommand: (state, action: PayloadAction<number>) => {
      if (action.payload >= 0 && action.payload < state.filteredCommands.length) {
        state.selectedIndex = action.payload
      }
    },
    addCommand: (state, action: PayloadAction<Command>) => {
      state.commands.push(action.payload)
      // Update categories
      if (!state.categories.includes(action.payload.category)) {
        state.categories.push(action.payload.category)
      }
      // Update filtered commands
      const query = state.searchQuery.toLowerCase()
      state.filteredCommands = state.commands.filter(command => 
        command.title.toLowerCase().includes(query) ||
        command.description.toLowerCase().includes(query) ||
        command.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
        command.category.toLowerCase().includes(query)
      )
    },
    removeCommand: (state, action: PayloadAction<string>) => {
      state.commands = state.commands.filter(cmd => cmd.id !== action.payload)
      // Update filtered commands
      const query = state.searchQuery.toLowerCase()
      state.filteredCommands = state.commands.filter(command => 
        command.title.toLowerCase().includes(query) ||
        command.description.toLowerCase().includes(query) ||
        command.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
        command.category.toLowerCase().includes(query)
      )
    },
    addRecentCommand: (state, action: PayloadAction<string>) => {
      // Remove if already exists
      state.recentCommands = state.recentCommands.filter(id => id !== action.payload)
      // Add to beginning
      state.recentCommands.unshift(action.payload)
      // Keep only last 10
      if (state.recentCommands.length > 10) {
        state.recentCommands = state.recentCommands.slice(0, 10)
      }
    },
    clearRecentCommands: (state) => {
      state.recentCommands = []
    },
    setCommands: (state, action: PayloadAction<Command[]>) => {
      state.commands = action.payload
      // Update categories
      state.categories = [...new Set(action.payload.map(cmd => cmd.category))]
      // Update filtered commands
      const query = state.searchQuery.toLowerCase()
      state.filteredCommands = state.commands.filter(command => 
        command.title.toLowerCase().includes(query) ||
        command.description.toLowerCase().includes(query) ||
        command.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
        command.category.toLowerCase().includes(query)
      )
    }
  }
})

export const {
  openCommandPalette,
  closeCommandPalette,
  setSearchQuery,
  selectNext,
  selectPrevious,
  selectCommand,
  addCommand,
  removeCommand,
  addRecentCommand,
  clearRecentCommands,
  setCommands
} = commandPaletteSlice.actions

export default commandPaletteSlice.reducer 