import DiseaseCard from './components/DiseaseCard'
import PriceCard from './components/PriceCard'
import SchemeCard from './components/SchemeCard'
import MarketCard from './components/MarketCard'

function App() {
  return (
    <div style={{ padding: '40px', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
      <h1 style={{ width: '100%' }}>Kisan Sathi</h1>
      <DiseaseCard />
      <PriceCard />
      <SchemeCard />
      <MarketCard />
    </div>
  )
}

export default App