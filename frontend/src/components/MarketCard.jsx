function MarketCard() {
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
      <div style={{ color: '#f57c00', fontWeight: 'bold', fontSize: '14px' }}>
        📈 MARKET ADVICE
      </div>
      <h2 style={{ margin: '8px 0' }}>Next Season — ಮುಂದಿನ ಋತು</h2>
      <p style={{ color: '#555', fontSize: '14px' }}>
        Based on 12-month APEDA trend analysis
      </p>
      <hr />
      <p><strong>Recommended Crop:</strong> Maize — ಮೆಕ್ಕೆ ಜೋಳ</p>
      <p><strong>Expected Price:</strong> ₹1,820 — ₹2,100/quintal</p>
      <p><strong>Demand:</strong> High — Export demand rising 18%</p>
      <p><strong>Best Market:</strong> Dharwad APMC</p>
      <p style={{ color: '#888', fontSize: '12px' }}>📍 Belagavi, Karnataka · 23 mins ago</p>
    </div>
  )
}

export default MarketCard