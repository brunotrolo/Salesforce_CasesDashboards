import React, { useState, FormEvent, Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import { reportApi } from '@api/reportApi'
import './styles/globals.css'

const DashboardPage = lazy(() => import('@pages/DashboardPage').then(m => ({ default: m.DashboardPage })))
const BuilderPage = lazy(() => import('@pages/BuilderPage').then(m => ({ default: m.BuilderPage })))
const AnalyticsPage = lazy(() => import('@pages/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })))

export const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('auth_token') !== null
  })
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const response = await reportApi.login(username, password)
      localStorage.setItem('auth_token', response.access_token)
      setIsLoggedIn(true)
    } catch (err) {
      setError('Credenciais inválidas. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setIsLoggedIn(false)
    setUsername('')
    setPassword('')
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="bg-card border border-border rounded-lg p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-primary-dark mb-1 text-center">Salesforce Reports</h1>
          <p className="text-muted-foreground mb-6 text-center">Dashboard de Relatórios Integrado</p>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                Usuário
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            {error && (
              <p role="alert" className="text-sm text-destructive bg-red-50 border border-red-200 rounded-md p-2">
                {error}
              </p>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white font-semibold py-2.5 rounded-md hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-background">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2 focus:rounded-md"
        >
          Pular para o conteúdo principal
        </a>
        <nav className="bg-card border-b border-border" aria-label="Navegação principal">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-8">
              <h1 className="text-xl font-bold text-primary">Reports</h1>
              <div className="flex gap-2">
                <NavLink
                  to="/"
                  end
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:text-primary hover:bg-muted'
                    }`
                  }
                >
                  Dashboard
                </NavLink>
                <NavLink
                  to="/builder"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:text-primary hover:bg-muted'
                    }`
                  }
                >
                  Criar Relatório
                </NavLink>
                <NavLink
                  to="/analytics"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:text-primary hover:bg-muted'
                    }`
                  }
                >
                  Análise
                </NavLink>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-card border border-border text-destructive px-4 py-2 rounded-md hover:bg-red-50 transition-colors cursor-pointer"
            >
              Sair
            </button>
          </div>
        </nav>

        <Suspense
          fallback={
            <div className="flex items-center justify-center min-h-[50vh]">
              <div className="animate-pulse text-muted-foreground">Carregando...</div>
            </div>
          }
        >
          <main id="main-content">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/builder" element={<BuilderPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </Suspense>
      </div>
    </Router>
  )
}

export default App