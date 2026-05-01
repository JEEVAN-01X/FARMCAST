function SchemeCard() {
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
      <div style={{ color: '#7b1fa2', fontWeight: 'bold', fontSize: '14px' }}>
        🏛️ GOVERNMENT SCHEME
      </div>
      <h2 style={{ margin: '8px 0' }}>PM-KISAN</h2>
      <p style={{ color: '#555', fontSize: '14px' }}>
        ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ
      </p>
      <hr />
      <p><strong>Benefit:</strong> ₹6,000/year in 3 installments</p>
      <p><strong>Eligibility:</strong> Small farmer, land &lt; 2 hectares</p>
      <p><strong>Documents:</strong> Aadhaar + Land record + Bank passbook</p>
      <p><strong>Apply:</strong> pmkisan.gov.in</p>
      <p style={{ color: '#888', fontSize: '12px' }}>📍 Mysuru, Karnataka · 15 mins ago</p>
    </div>
  )
}

export default SchemeCard