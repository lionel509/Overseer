import React from 'react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'chat', label: 'Chat', icon: <img
      src="https://img.icons8.com/?size=100&id=59753&format=png&color=018141"
      alt="Chat"
      width={24}
      height={24}
      style={{ marginRight: 12 }}
    />},
    { id: 'dashboard', label: 'Dashboard', icon: <img
      src="https://img.icons8.com/?size=100&id=uWyVYfqqdYxW&format=png&color=018141"
      alt="Dashboard"
      width={24}
      height={24}
      style={{ marginRight: 12 }}
    />},
    { id: 'files', label: 'Files', icon: <img
      src="https://img.icons8.com/?size=100&id=83170&format=png&color=018141"
      alt="Files"
      width={24}
      height={24}
      style={{ marginRight: 12 }}
    />}
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Overseer</h1>
        <p className="sidebar-subtitle">System Assistant</p>
      </div>
      <nav className="sidebar-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`sidebar-tab${activeTab === tab.id ? ' sidebar-tab-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="sidebar-tab-icon">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="sidebar-status-dot"></span>
          <span>Connected</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar