import { useState, useRef, useEffect } from 'react'
import './InputArea.css'

function InputArea({ onSendMessage, loading }) {
  const [input, setInput] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !loading) {
      onSendMessage(input)
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          ref={textareaRef}
          className="input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about NIT Kurukshetra..."
          rows={1}
          disabled={loading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!input.trim() || loading}
        >
          {loading ? <span className="button-loading">⏳</span> : <span>➤</span>}
        </button>
      </div>
      <div className="input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </form>
  )
}

export default InputArea
