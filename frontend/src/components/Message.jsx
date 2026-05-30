import { useState } from 'react'
import './Message.css'

function Message({ message }) {
  const [showSources, setShowSources] = useState(false)
  const [showTrace, setShowTrace] = useState(false)
  
  const isBot = message.type === 'bot'
  const hasSources = message.sources && message.sources.length > 0
  const metadata = message.metadata

  return (
    <div className={`message ${isBot ? 'message-bot' : 'message-user'}`}>
      <div className="message-avatar">
        {isBot ? '🤖' : '👤'}
      </div>
      <div className="message-content">
        <div className={`message-bubble ${message.error ? 'message-error' : ''}`}>
          <p className="message-text">{message.content}</p>
          
          {isBot && metadata && (
            <div className="message-metadata">
              <div className="metadata-badges">
                <span className="metadata-badge intent" title={`Reasoning: ${metadata.reasoning}`}>
                  🎯 {metadata.intent}
                </span>
                {metadata.iterations > 1 && (
                  <span className="metadata-badge iterations">
                    🔄 {metadata.iterations} iterations
                  </span>
                )}
                <span className="metadata-badge time">
                  ⏱️ {metadata.execution_time.toFixed(2)}s
                </span>
                <span className="metadata-badge quality" style={{ opacity: metadata.quality_score }}>
                  ⭐ {Math.round(metadata.quality_score * 100)}% Match
                </span>
              </div>
              
              {metadata.tools_used && metadata.tools_used.length > 0 && (
                <div className="metadata-tools">
                  <button 
                    className="trace-toggle"
                    onClick={() => setShowTrace(!showTrace)}
                  >
                    {showTrace ? 'Hide Trace' : 'View Trace'}
                  </button>
                  {showTrace && (
                    <div className="tools-list">
                      <strong>Tools invoked:</strong> {metadata.tools_used.join(' → ')}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

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
                        {source.score > 0 && (
                          <span className="source-score">
                            Relevance: {source.score.toFixed(3)}
                          </span>
                        )}
                      </div>
                      {source.url !== '#' && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="source-url"
                        >
                          {source.url}
                        </a>
                      )}
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

