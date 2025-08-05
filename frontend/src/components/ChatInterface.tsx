import React, { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your system assistant. How can I help you today?",
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }
    
    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showMenu])

  const handleMenuAction = (action: string) => {
    setShowMenu(false)
    
    switch (action) {
      case 'clear':
        setMessages([{
          id: '1',
          type: 'assistant',
          content: "Hello! I'm your system assistant. How can I help you today?",
          timestamp: new Date()
        }])
        break
      case 'export':
        const chatData = messages.map(msg => ({
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp.toISOString()
        }))
        const dataStr = JSON.stringify(chatData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`
        link.click()
        URL.revokeObjectURL(url)
        break
      case 'search':
        const searchTerm = prompt('Search messages for:')
        if (searchTerm) {
          const matchingMessages = messages.filter(msg => 
            msg.content.toLowerCase().includes(searchTerm.toLowerCase())
          )
          if (matchingMessages.length > 0) {
            alert(`Found ${matchingMessages.length} messages containing "${searchTerm}"`)
          } else {
            alert(`No messages found containing "${searchTerm}"`)
          }
        }
        break
      case 'settings':
        alert('Settings functionality would open here')
        break
      case 'help':
        const helpMessage: Message = {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Here are some things you can ask me about:
• System monitoring and performance
• File management operations
• Process management
• System configuration
• Troubleshooting assistance
• Security monitoring

You can also use the menu (⋯) for additional options like clearing chat history, exporting conversations, or searching messages.`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, helpMessage])
        break
      default:
        break
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate API call
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I understand you're asking about: "${inputValue}". This is a simulated response. In a real implementation, this would connect to your Overseer backend.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-root">
      <div className="chat-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h2 className="chat-title">System Assistant</h2>
            <p className="chat-desc">Ask me anything about your system</p>
          </div>
          <div style={{ position: 'relative' }} ref={menuRef}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              style={{
                background: 'none',
                border: 'none',
                color: '#b6ffb6',
                fontSize: '1.5rem',
                cursor: 'pointer',
                padding: '0.5rem',
                borderRadius: '50%',
                transition: 'background 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '40px',
                height: '40px'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
              aria-label="Menu"
            >
              ⋯
            </button>
            {showMenu && (
              <div style={{
                position: 'absolute',
                top: '100%',
                right: '0',
                background: '#16281a',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                zIndex: 1000,
                minWidth: '180px',
                padding: '0.5rem 0'
              }}>
                <button
                  onClick={() => handleMenuAction('clear')}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'none',
                    border: 'none',
                    color: '#e6ffe6',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  🗑️ Clear Chat
                </button>
                <button
                  onClick={() => handleMenuAction('export')}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'none',
                    border: 'none',
                    color: '#e6ffe6',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  📤 Export Chat
                </button>
                <button
                  onClick={() => handleMenuAction('search')}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'none',
                    border: 'none',
                    color: '#e6ffe6',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  🔍 Search Messages
                </button>
                <div style={{
                  height: '1px',
                  background: '#2e8b57',
                  margin: '0.5rem 0'
                }}></div>
                <button
                  onClick={() => handleMenuAction('settings')}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'none',
                    border: 'none',
                    color: '#e6ffe6',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  ⚙️ Settings
                </button>
                <button
                  onClick={() => handleMenuAction('help')}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'none',
                    border: 'none',
                    color: '#e6ffe6',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(76, 255, 128, 0.1)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                  ❓ Help
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`chat-bubble ${message.type === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}>
            <div className="chat-content">{message.content}</div>
            <div className="chat-timestamp">{message.timestamp.toLocaleTimeString()}</div>
          </div>
        ))}
        {isLoading && (
          <div className="chat-bubble chat-bubble-assistant">
            <div className="chat-typing">
              <span className="chat-dot"></span>
              <span className="chat-dot" style={{ animationDelay: '0.2s' }}></span>
              <span className="chat-dot" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-bar" onSubmit={e => { e.preventDefault(); handleSendMessage(); }}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask about system monitoring, file management, or any system task..."
          disabled={isLoading}
          className="chat-textarea"
          onKeyDown={handleKeyPress}
          rows={1}
        />
        <button
          type="submit"
          className="chat-send-btn"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatInterface 