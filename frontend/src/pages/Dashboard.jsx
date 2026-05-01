import LiveAlert from '../components/LiveAlert'
import FarmerMap from '../components/FarmerMap'
import DiseaseCard from '../components/DiseaseCard'
import PriceCard from '../components/PriceCard'
import SchemeCard from '../components/SchemeCard'
import MarketCard from '../components/MarketCard'

const stats = [
  { label: 'Total Calls Today', value: '1,247', color: '#1976d2' },
  { label: 'Resolved', value: '89', color: '#2e7d32' },
  { label: 'Active Now', value: '3', color: '#e53935' },
  { label: 'Schemes Matched', value: '234', color: '#7b1fa2' }
]

const recentCalls = [
  { farmer: 'Ramu Naik', query: 'ಟೊಮೇಟೊ ರೋಗ', time: '2 mins ago', location: 'Kolar' },
  { farmer: 'Suresh Patil', query: 'ಮಂಡಿ ಬೆಲೆ', time: '8 mins ago', location: 'Dharwad' },
  { farmer: 'Lakshmi Devi', query: 'ಸರ್ಕಾರಿ ಯೋಜನೆ', time: '15 mins ago', location: 'Mysuru' },
  { farmer: 'Anjaiah', query: 'ಮಾರುಕಟ್ಟೆ ಸಲಹೆ', time: '23 mins ago', location: 'Belagavi' }
]

function Dashboard() {
  return (
    <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: '30px' }}>

      <LiveAlert />

      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ margin: 0, color: '#1a1a1a' }}>🌾 Kisan Sathi — KVK Dashboard</h1>
        <p style={{ color: '#666', margin: '4px 0 0' }}>Live farmer call monitoring · Karnataka</p>
      </div>

      {/* Stats Row */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '30px', flexWrap: 'wrap' }}>
        {stats.map((stat) => (
          <div key={stat.label} style={{
            backgroundColor: '#fff',
            borderRadius: '12px',
            padding: '20px 28px',
            flex: '1',
            minWidth: '150px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
          }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: stat.color }}>{stat.value}</div>
            <div style={{ color: '#888', fontSize: '13px', marginTop: '4px' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Recent Calls */}
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '30px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <h2 style={{ margin: '0 0 16px', fontSize: '16px' }}>📞 Recent Farmer Calls</h2>
        {recentCalls.map((call, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 0',
            borderBottom: i < recentCalls.length - 1 ? '1px solid #f0f0f0' : 'none'
          }}>
            <div>
              <strong>{call.farmer}</strong>
              <span style={{ color: '#555', fontSize: '14px', marginLeft: '12px' }}>{call.query}</span>
            </div>
            <div style={{ color: '#888', fontSize: '13px' }}>
              📍 {call.location} · {call.time}
            </div>
          </div>
        ))}
      </div>

      {/* Map */}
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '30px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
      }}>
        <h2 style={{ margin: '0 0 16px', fontSize: '16px' }}>🗺️ Farmer Call Locations</h2>
        <FarmerMap />
      </div>

      {/* WhatsApp Cards */}
      <h2 style={{ fontSize: '16px', marginBottom: '16px' }}>📲 WhatsApp Responses Sent</h2>
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <DiseaseCard />
        <PriceCard />
        <SchemeCard />
        <MarketCard />
      </div>

    </div>
  )
}

export default Dashboard