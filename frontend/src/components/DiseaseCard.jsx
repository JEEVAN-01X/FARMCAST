function DiseaseCard() {
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
      <div style={{ color: '#e53935', fontWeight: 'bold', fontSize: '14px' }}>
        🌿 DISEASE ALERT
      </div>
      <h2 style={{ margin: '8px 0' }}>Jowar Anthracnose</h2>
      <p style={{ color: '#555', fontSize: '14px' }}>
        ಬಿಳಿ ಚುಕ್ಕೆ ರೋಗ — White spots on leaves
      </p>
      <hr />
      <p><strong>Treatment:</strong> Spray Mancozeb 75% WP @ 2g/litre</p>
      <p><strong>Nearest Shop:</strong> Haveri Agri Centre — 2.3 km</p>
      <p style={{ color: '#888', fontSize: '12px' }}>📍 Haveri, Karnataka · 2 mins ago</p>
    </div>
  )
}

export default DiseaseCard