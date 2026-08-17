import React, { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface AnalyticsData {
  date: string
  reports: number
  views: number
  updates: number
}

const generateMockData = (): AnalyticsData[] => [
  { date: '01/12', reports: 24, views: 120, updates: 5 },
  { date: '02/12', reports: 28, views: 140, updates: 7 },
  { date: '03/12', reports: 32, views: 160, updates: 8 },
  { date: '04/12', reports: 35, views: 180, updates: 9 },
  { date: '05/12', reports: 40, views: 200, updates: 11 },
  { date: '06/12', reports: 45, views: 230, updates: 13 }
]

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData[]>([])

  useEffect(() => {
    setData(generateMockData())
  }, [])

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-primary-dark mb-8">Análise de Relatórios</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-card border border-border rounded-lg p-6">
            <p className="text-sm text-muted-foreground font-semibold">Total de Relatórios</p>
            <p className="text-3xl font-bold text-primary mt-2">245</p>
            <p className="text-xs text-success mt-2">↑ 12% este mês</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6">
            <p className="text-sm text-muted-foreground font-semibold">Visualizações</p>
            <p className="text-3xl font-bold text-primary mt-2">1.2K</p>
            <p className="text-xs text-success mt-2">↑ 23% esta semana</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6">
            <p className="text-sm text-muted-foreground font-semibold">Taxa de Atualização</p>
            <p className="text-3xl font-bold text-destructive mt-2">8.5%</p>
            <p className="text-xs text-destructive mt-2">↓ 2% desde ontem</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Crescimento de Relatórios</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="reports" stroke="#1E40AF" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Atividade</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="views" fill="#3B82F6" />
                <Bar dataKey="updates" fill="#D97706" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}