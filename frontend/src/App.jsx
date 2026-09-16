import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import ResumeUpload from './pages/ResumeUpload'
import Interview from './pages/Interview'
import Report from './pages/Report'

function RequireAuth({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" />
}

function NavBar() {
  const navigate = useNavigate()
  const token = localStorage.getItem('token')

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav>
      <div>
        <Link to="/upload">AI Interview Simulator</Link>
      </div>
      {token && <button className="secondary" onClick={logout}>Log out</button>}
    </nav>
  )
}

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Navigate to="/upload" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/upload" element={<RequireAuth><ResumeUpload /></RequireAuth>} />
        <Route path="/interview" element={<RequireAuth><Interview /></RequireAuth>} />
        <Route path="/report" element={<RequireAuth><Report /></RequireAuth>} />
      </Routes>
    </>
  )
}
