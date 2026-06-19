import { HashRouter as BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { AuthProvider, useAuth } from './context/AuthContext'
import { LangProvider } from './context/LangContext'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import AnalyzePage from './pages/AnalyzePage'
import ResultPage from './pages/ResultPage'
import HistoryPage from './pages/HistoryPage'

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 size={28} className="animate-spin text-health-400" />
    </div>
  )
  return token ? children : <Navigate to="/auth" replace />
}

function AppRoutes() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"           element={<LandingPage />} />
        <Route path="/auth"       element={<AuthPage />} />
        <Route path="/analyze"    element={<ProtectedRoute><AnalyzePage /></ProtectedRoute>} />
        <Route path="/result/:id" element={<ProtectedRoute><ResultPage /></ProtectedRoute>} />
        <Route path="/history"    element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
        <Route path="*"           element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <LangProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </LangProvider>
  )
}
