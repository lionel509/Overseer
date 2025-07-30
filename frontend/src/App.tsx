import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import SystemDashboard from './components/SystemDashboard'
import FileManager from './components/FileManager'
import Sidebar from './components/Sidebar'
import Settings from './components/Settings'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="app-main">
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1em' }}>
          <button
            aria-label="Settings"
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
            onClick={() => setShowSettings(true)}
          >
            {/* Settings icon from icons8 */}
            <img
              src="https://img.icons8.com/?size=100&id=2969&format=png&color=000000"
              alt="Settings"
              width={28}
              height={28}
              style={{ display: 'block', filter: 'invert(54%) sepia(98%) saturate(749%) hue-rotate(86deg) brightness(104%) contrast(101%)' }}
            />
          </button>
        </div>
        {showSettings && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(0,0,0,0.45)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div style={{ position: 'relative', background: '#16281a', borderRadius: 12, boxShadow: '0 4px 32px #0008', padding: '2em', minWidth: 340, maxWidth: '90vw' }}>
              <button
                aria-label="Close settings"
                onClick={() => setShowSettings(false)}
                style={{
                  position: 'absolute',
                  top: 12,
                  right: 12,
                  background: 'none',
                  border: 'none',
                  fontSize: 24,
                  color: '#b6ffb6',
                  cursor: 'pointer',
                  zIndex: 10,
                }}
              >
                ×
              </button>
              <Settings />
            </div>
          </div>
        )}
        {!showSettings && (
          <>
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'dashboard' && <SystemDashboard />}
            {activeTab === 'files' && <FileManager />}
          </>
        )}
      </main>
    </div>
  )
}

export default App
