import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import { DashboardPage } from '@pages/DashboardPage'
import { BuilderPage } from '@pages/BuilderPage'
import { AnalyticsPage } from '@pages/AnalyticsPage'
import './styles/globals.css'

export const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('token') !== null
  })

  const handleLogin = () => {
    localStorage.setItem('token', 'demo-token')
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsLoggedIn(false)
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">Salesforce Reports</h1>
          <p className="text-gray-600 mb-6 text-center">Dashboard de Relatórios Integrado</p>
          <button
            onClick={handleLogin}
            className="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Fazer Login
          </button>
          <p className="text-xs text-gray-500 mt-4 text-center">
            Demo: Clique para acessar com credenciais de teste
          </p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-8">
              <h1 className="text-2xl font-bold text-indigo-600">Reports</h1>
              <div className="flex gap-6">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/builder"
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors"
                >
                  Criar Relatório
                </Link>
                <Link
                  to="/analytics"
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors"
                >
                  Análise
                </Link>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
            >
              Sair
            </button>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
