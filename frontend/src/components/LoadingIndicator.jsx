import './LoadingIndicator.css'

function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="loading-avatar">🤖</div>
      <div className="loading-content">
        <div className="loading-bubble">
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingIndicator

