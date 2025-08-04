import React from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { openCommandPalette } from '../store/commandPaletteSlice'
import { toggleSidebar } from '../store/appSlice'
import { 
  Menu, 
  Search, 
  Command, 
  Settings, 
  Bell, 
  User,
  Sun,
  Moon
} from 'lucide-react'

const Header: React.FC = () => {
  const dispatch = useAppDispatch()
  const { theme, sidebarCollapsed } = useAppSelector(state => state.app)

  const handleToggleSidebar = () => {
    dispatch(toggleSidebar())
  }

  const handleOpenCommandPalette = () => {
    dispatch(openCommandPalette())
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={handleToggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">O</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Overseer</span>
          </div>
        </div>

        {/* Center - Search */}
        <div className="flex-1 max-w-md mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search or press Cmd+K..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onFocus={handleOpenCommandPalette}
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleOpenCommandPalette}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Command className="w-4 h-4" />
            <span className="hidden sm:inline">Commands</span>
          </button>

          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
          </button>

          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Settings className="w-5 h-5 text-gray-600" />
          </button>

          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-gray-600" />
            ) : (
              <Moon className="w-5 h-5 text-gray-600" />
            )}
          </button>

          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600" />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 