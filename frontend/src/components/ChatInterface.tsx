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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

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
        <h2 className="chat-title">System Assistant</h2>
        <p className="chat-desc">Ask me anything about your system</p>
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