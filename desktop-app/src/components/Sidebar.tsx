import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAppSelector } from '../store/hooks'
import { 
  Home, 
  Folder, 
  Settings, 
  Activity, 
  Server, 
  Database,
  FileText,
  Users,
  Shield,
  Command,
  Lightbulb,
  BarChart3
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const location = useLocation()
  const { sidebarCollapsed } = useAppSelector(state => state.app)

  const navigationItems = [
    {
      name: 'Dashboard',
      icon: Home,
      path: '/dashboard',
      description: 'System overview'
    },
    {
      name: 'File Search',
      icon: Folder,
      path: '/files',
      description: 'File search & management'
    },
    {
      name: 'Commands',
      icon: Command,
      path: '/commands',
      description: 'Command processor'
    },
    {
      name: 'Tool Recommender',
      icon: Lightbulb,
      path: '/tools',
      description: 'Smart tool suggestions'
    },
    {
      name: 'Real-time Stats',
      icon: BarChart3,
      path: '/stats',
      description: 'Live system analytics'
    },
    {
      name: 'Monitoring',
      icon: Activity,
      path: '/monitoring',
      description: 'System monitoring'
    },
    {
      name: 'Settings',
      icon: Settings,
      path: '/settings',
      description: 'Application settings'
    },
    {
      name: 'Backend',
      icon: Server,
      path: '/backend',
      description: 'Python backend'
    },
    {
      name: 'Database',
      icon: Database,
      path: '/database',
      description: 'Data management'
    },
    {
      name: 'Documents',
      icon: FileText,
      path: '/documents',
      description: 'Documentation'
    },
    {
      name: 'Users',
      icon: Users,
      path: '/users',
      description: 'User management'
    },
    {
      name: 'Security',
      icon: Shield,
      path: '/security',
      description: 'Security settings'
    }
  ]

  if (sidebarCollapsed) {
    return (
      <aside className="w-16 bg-white border-r border-gray-200 flex flex-col">
        <div className="flex-1 py-4">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center justify-center p-3 mb-2 mx-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                title={item.name}
              >
                <Icon className="w-5 h-5" />
              </Link>
            )
          })}
        </div>
      </aside>
    )
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="flex-1 py-4">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 mx-2 mb-1 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-100 text-blue-600' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-5 h-5" />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs text-gray-500">{item.description}</div>
              </div>
            </Link>
          )
        })}
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Overseer Desktop v1.0.0
        </div>
      </div>
    </aside>
  )
}

export default Sidebar 