export const demoScenarios = [
  {
    id: 1,
    farmer: 'Ramu Naik',
    phone: '+91 94481 23456',
    location: 'Kolar',
    lat: 13.1368,
    lng: 78.1298,
    query: 'ಟೊಮೇಟೊ ರೋಗ',
    queryEnglish: 'Tomato Disease',
    type: 'disease',
    time: '2 mins ago',
    status: 'resolved',
    response: 'Spray Mancozeb 75% WP @ 2g/litre'
  },
  {
    id: 2,
    farmer: 'Suresh Patil',
    phone: '+91 98765 43210',
    location: 'Dharwad',
    lat: 15.3647,
    lng: 75.1240,
    query: 'ಮಂಡಿ ಬೆಲೆ',
    queryEnglish: 'Mandi Price',
    type: 'price',
    time: '8 mins ago',
    status: 'resolved',
    response: 'Tomato ₹2,840/quintal at Dharwad APMC'
  },
  {
    id: 3,
    farmer: 'Lakshmi Devi',
    phone: '+91 87654 32109',
    location: 'Mysuru',
    lat: 12.2958,
    lng: 76.6394,
    query: 'ಸರ್ಕಾರಿ ಯೋಜನೆ',
    queryEnglish: 'Government Scheme',
    type: 'scheme',
    time: '15 mins ago',
    status: 'resolved',
    response: 'PM-KISAN ₹6,000/year — eligible'
  },
  {
    id: 4,
    farmer: 'Anjaiah',
    phone: '+91 76543 21098',
    location: 'Belagavi',
    lat: 15.8497,
    lng: 74.4977,
    query: 'ಮಾರುಕಟ್ಟೆ ಸಲಹೆ',
    queryEnglish: 'Market Advice',
    type: 'market',
    time: '23 mins ago',
    status: 'resolved',
    response: 'Next season — grow Maize, good demand'
  }
]

export const liveStats = {
  totalCallsToday: 1247,
  resolved: 89,
  activeNow: 3,
  schemesMatched: 234
}