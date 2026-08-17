import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ResultsPage } from '@pages/ResultsPage'
import './styles/globals.css'

export const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ResultsPage />} />
        <Route path="/results/:id" element={<ResultsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
