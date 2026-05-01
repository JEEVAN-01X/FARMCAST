import { useState, useEffect } from 'react'

const alertMessages = [
  { farmer: 'Ramu Naik', query: 'ಟೊಮೇಟೊ ರೋಗ', location: 'Kolar', type: '🌿 Disease' },
  { farmer: 'Suresh Patil', query: 'ಮಂಡಿ ಬೆಲೆ', location: 'Dharwad', type: '💰 Price' },
  { farmer: 'Lakshmi Devi', query: 'ಸರ್ಕಾರಿ ಯೋಜನೆ', location: 'Mysuru', type: '🏛️ Scheme' },
  { farmer: 'Anjaiah', query: 'ಮಾರುಕಟ್ಟೆ ಸಲಹೆ', location: 'Belagavi', type: '📊 Market' }
]

function LiveAlert() {
  const [currentAlert, setCurrentAlert] = useState(null)
  const [visible, setVisible] = useState(false)
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentAlert(alertMessages[index % alertMessages.length])
      setVisible(true)
      setIndex(prev => prev + 1)

      setTimeout(() => setVisible(false), 4000)
    }, 6000)

    return () => clearInterval(interval)
  }, [index])

  if (!visible || !currentAlert) return null

  return (
    <div style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      backgroundColor: '#1b5e20',
      color: '#fff',
      padding: '14px 20px',
      borderRadius: '12px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.25)',
      zIndex: 9999,
      minWidth: '280px',
      animation: 'slideIn 0.4s ease'
    }}>
      <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '4px' }}>
        🔴 LIVE CALL · {currentAlert.type}
      </div>
      <div style={{ fontWeight: 'bold', fontSize: '15px' }}>{currentAlert.farmer}</div>
      <div style={{ fontSize: '13px', opacity: 0.9 }}>
        {currentAlert.query} · 📍 {currentAlert.location}
      </div>
    </div>
  )
}

export default LiveAlert