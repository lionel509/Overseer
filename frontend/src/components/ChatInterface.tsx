import React, { useState, useRef, useEffect } from 'react';
import { sendMessageToAI } from '../api';
import { useAuthInfo } from '@propelauth/react';

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

  const { accessToken } = useAuthInfo();

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let res;
      if (inputValue.trim().startsWith('sudo') || inputValue.trim().startsWith('run as root')) {
        res = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {})
          },
          body: JSON.stringify({ message: inputValue })
        });
        if (!res.ok) throw new Error('Failed to run sudo command');
        res = await res.json();
      } else {
        res = await sendMessageToAI(inputValue);
      }
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: res.reply || 'No response from AI.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (e) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 2).toString(),
        type: 'assistant',
        content: 'Error: Unable to get response from AI backend.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-root">
      <div className="chat-header">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
          <h2 className="chat-title" style={{ textAlign: 'center', width: '100%' }}>System Assistant</h2>
          <p className="chat-desc" style={{ textAlign: 'center', width: '100%' }}>Ask me anything about your system</p>
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