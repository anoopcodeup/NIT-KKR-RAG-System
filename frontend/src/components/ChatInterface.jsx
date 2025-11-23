import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import InputArea from './InputArea'
import { queryRAG } from '../services/api'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (query) => {
    if (!query.trim() || loading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await queryRAG(query)
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        sources: response.sources,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error querying RAG:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error processing your query. Please try again.',
        error: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="6" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                <rect x="6" y="9" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.6"/>
                <rect x="11" y="9" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.6"/>
                <rect x="15" y="9" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.6"/>
                <path d="M8 15H16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M12 2V6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M12 18V22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.1"/>
              </svg>
            </div>
            <h2 className="welcome-title">NIT KKR RAG Assistant</h2>
            <p className="welcome-subtitle">Ask me anything about NIT Kurukshetra</p>
            <div className="welcome-suggestions">
              <div 
                className="suggestion-chip" 
                onClick={() => handleSendMessage("What are the admission requirements?")}
              >
                What are the admission requirements?
              </div>
              <div 
                className="suggestion-chip" 
                onClick={() => handleSendMessage("Tell me about the departments")}
              >
                Tell me about the departments
              </div>
              <div 
                className="suggestion-chip" 
                onClick={() => handleSendMessage("What facilities are available?")}
              >
                What facilities are available?
              </div>
            </div>
          </div>
        ) : (
          <>
            <MessageList messages={messages} loading={loading} />
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      <InputArea onSendMessage={handleSendMessage} loading={loading} />
    </div>
  )
}

export default ChatInterface
