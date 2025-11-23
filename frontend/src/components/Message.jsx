import { useState } from 'react'
import './Message.css'

function Message({ message }) {
  const [showSources, setShowSources] = useState(false)
  const isBot = message.type === 'bot'
  const hasSources = message.sources && message.sources.length > 0

  return (
    <div className={`message ${isBot ? 'message-bot' : 'message-user'}`}>
      <div className="message-avatar">
        {isBot ? '🤖' : '👤'}
      </div>
      <div className="message-content">
        <div className={`message-bubble ${message.error ? 'message-error' : ''}`}>
          <p className="message-text">{message.content}</p>
          {hasSources && (
            <div className="message-sources">
              <button
                className="sources-toggle"
                onClick={() => setShowSources(!showSources)}
              >
                {showSources ? '▼' : '▶'} {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
              </button>
              {showSources && (
                <div className="sources-list">
                  {message.sources.map((source, index) => (
                    <div key={index} className="source-item">
                      <div className="source-header">
                        <span className="source-title">{source.title}</span>
                        <span className="source-score">
                          {source.score_type === 'rerank' ? 'Rerank' : 'Relevance'}: {source.score.toFixed(3)}
                        </span>
                      </div>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-url"
                      >
                        {source.url}
                      </a>
                      <p className="source-preview">{source.content_preview}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <span className="message-time">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}

export default Message

