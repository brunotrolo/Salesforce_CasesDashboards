import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { BuilderPage } from '@pages/BuilderPage'
import './styles/globals.css'

export const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<BuilderPage />} />
        <Route path="/builder" element={<BuilderPage />} />
        <Route path="/builder/:id" element={<BuilderPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
