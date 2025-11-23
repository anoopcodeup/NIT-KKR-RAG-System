import './StatsPanel.css'

function StatsPanel({ stats, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="stats-panel">
        <div className="stats-header">
          <h2>System Statistics</h2>
        </div>
        <div className="stats-loading">Loading...</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="stats-panel">
        <div className="stats-header">
          <h2>System Statistics</h2>
        </div>
        <div className="stats-error">Unable to load statistics</div>
      </div>
    )
  }

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <h2>System Statistics</h2>
        <button className="refresh-button" onClick={onRefresh} title="Refresh">
          ↻
        </button>
      </div>
      <div className="stats-content">
        {[
          { label: 'Total Chunks', value: stats.total_chunks },
          { label: 'Documents', value: stats.unique_documents },
          { label: 'Total Words', value: stats.total_words },
          { label: 'Avg Chunk Length', value: stats.average_chunk_length.toFixed(0) + ' words' }
        ].map((item, index) => (
          <div key={index} className="stat-item">
            <div className="stat-label">{item.label}</div>
            <div className="stat-value">{item.value.toLocaleString?.() ?? item.value}</div>
          </div>
        ))}
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-label">Embedding Model</div>
          <div className="stat-value-small">{stats.model_name}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Dimension</div>
          <div className="stat-value-small">{stats.embedding_dimension}</div>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-label">Groq LLM</div>
          <div className={`stat-badge ${stats.groq_available ? 'stat-badge-success' : 'stat-badge-error'}`}>
            {stats.groq_available ? '✓ Enabled' : '✗ Disabled'}
          </div>
        </div>
        {stats.groq_model && (
          <div className="stat-item">
            <div className="stat-label">Groq Model</div>
            <div className="stat-value-small">{stats.groq_model}</div>
          </div>
        )}
        <div className="stat-item">
          <div className="stat-label">Reranker</div>
          <div className={`stat-badge ${stats.reranker_enabled ? 'stat-badge-success' : 'stat-badge-warning'}`}>
            {stats.reranker_enabled ? '✓ Enabled' : '⚠ Disabled'}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel
