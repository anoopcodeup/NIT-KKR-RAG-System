import './StatsPanel.css'

function StatsPanel({ stats, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="stats-panel">
        <div className="stats-header">
          <h2>System Intelligence</h2>
        </div>
        <div className="stats-loading">Initializing Agents...</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="stats-panel">
        <div className="stats-header">
          <h2>System Intelligence</h2>
        </div>
        <div className="stats-error">Agentic Brain Offline</div>
      </div>
    )
  }

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <h2>System Intelligence</h2>
        <button className="refresh-button" onClick={onRefresh} title="Sync">
          ↻
        </button>
      </div>
      <div className="stats-content">
        <div className="stat-item">
          <div className="stat-label">Status</div>
          <div className={`stat-badge ${stats.status === 'active' ? 'stat-badge-success' : 'stat-badge-warning'}`}>
            {stats.status.toUpperCase()}
          </div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">Active Agents</div>
          <div className="stat-value">{stats.agents_online}</div>
        </div>

        <div className="stat-divider"></div>
        
        <div className="stat-item">
          <div className="stat-label">Queries Processed</div>
          <div className="stat-value">{stats.total_queries_processed}</div>
        </div>

        <div className="stat-item">
          <div className="stat-label">Avg. Latency</div>
          <div className="stat-value">{stats.average_latency.toFixed(2)}s</div>
        </div>

        <div className="stat-divider"></div>

        <div className="stat-item">
          <div className="stat-label">Model Architecture</div>
          <div className="stat-value-small">{stats.groq_model}</div>
        </div>

        <div className="stat-divider"></div>

        <div className="stat-item tools-section">
          <div className="stat-label">Capabilities</div>
          <div className="tools-badges">
            {stats.tools_available.map((tool, index) => (
              <span key={index} className="tool-chip">
                {tool.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel
