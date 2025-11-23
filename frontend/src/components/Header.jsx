import './Header.css'

function Header({ darkMode, setDarkMode }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h1>NIT KKR RAG Assistant</h1>
          <p className="header-subtitle">Ask questions about NIT Kurukshetra</p>
        </div>
        <div className="header-actions">
          <div className="header-badge">
            <span className="badge-dot"></span>
            <span>Powered by RAG</span>
          </div>
          <button
            className="dark-mode-toggle"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
