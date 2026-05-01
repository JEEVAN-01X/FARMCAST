function PriceCard() {
  return (
    <div style={{
      backgroundColor: '#fff',
      border: '1px solid #e0e0e0',
      borderRadius: '12px',
      padding: '20px',
      maxWidth: '400px',
      fontFamily: 'sans-serif',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <div style={{ color: '#1976d2', fontWeight: 'bold', fontSize: '14px' }}>
        💰 MANDI PRICE
      </div>
      <h2 style={{ margin: '8px 0' }}>Tomato — ಟೊಮೇಟೊ</h2>
      <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#1976d2', margin: '8px 0' }}>
        ₹2,840 <span style={{ fontSize: '14px', color: '#888' }}>/quintal</span>
      </p>
      <hr />
      <p><strong>Market:</strong> Kolar APMC</p>
      <p style={{ color: '#2e7d32', fontWeight: 'bold' }}>↑ +12% vs last month</p>
      <p style={{ color: '#888', fontSize: '12px' }}>📍 Kolar, Karnataka · Today 6:00 AM</p>
    </div>
  )
}

export default PriceCard