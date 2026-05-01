import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const farmerLocations = [
  { id: 1, name: 'Ramu Naik', query: 'ಟೊಮೇಟೊ ರೋಗ', lat: 13.1368, lng: 78.1298, city: 'Kolar' },
  { id: 2, name: 'Suresh Patil', query: 'ಮಂಡಿ ಬೆಲೆ', lat: 15.3647, lng: 75.1240, city: 'Dharwad' },
  { id: 3, name: 'Lakshmi Devi', query: 'ಸರ್ಕಾರಿ ಯೋಜನೆ', lat: 12.2958, lng: 76.6394, city: 'Mysuru' },
  { id: 4, name: 'Anjaiah', query: 'ಮಾರುಕಟ್ಟೆ ಸಲಹೆ', lat: 15.8497, lng: 74.4977, city: 'Belagavi' }
]

function FarmerMap() {
  return (
    <MapContainer
      center={[15.3173, 75.7139]}
      zoom={6}
      style={{ height: '400px', width: '100%', borderRadius: '12px' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="© OpenStreetMap contributors"
      />
      {farmerLocations.map((farmer) => (
        <Marker key={farmer.id} position={[farmer.lat, farmer.lng]}>
          <Popup>
            <div style={{ fontFamily: 'sans-serif', minWidth: '150px' }}>
              <strong>{farmer.name}</strong>
              <p style={{ margin: '4px 0', color: '#555' }}>{farmer.query}</p>
              <p style={{ margin: 0, color: '#888', fontSize: '12px' }}>
                📍 {farmer.city}, Karnataka
              </p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}

export default FarmerMap