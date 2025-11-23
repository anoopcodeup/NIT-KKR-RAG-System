import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import StatsPanel from './components/StatsPanel'
import './App.css'

function App() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />
      <div className="app-container">
        <div className="app-main">
          <ChatInterface />
        </div>
        <div className="app-sidebar">
          <StatsPanel stats={stats} loading={loading} onRefresh={fetchStats} />
        </div>
      </div>
    </div>
  )
}

export default App
