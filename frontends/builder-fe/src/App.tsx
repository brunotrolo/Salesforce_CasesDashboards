import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { BuilderPage } from '@pages/BuilderPage'
import './styles/globals.css'

export const App: React.FC = () => {
  return (
    <Router>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2 focus:rounded-md"
      >
        Pular para o conteúdo principal
      </a>
      <main id="main-content">
        <Routes>
          <Route path="/" element={<BuilderPage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/builder/:id" element={<BuilderPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </Router>
  )
}

export default App
