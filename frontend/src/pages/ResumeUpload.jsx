import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function ResumeUpload() {
  const [file, setFile] = useState(null)
  const [targetRole, setTargetRole] = useState('')
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!file) return setError('Please choose a resume file (PDF, DOCX, or TXT).')
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('target_role', targetRole)
      const { data } = await api.post('/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      navigate('/interview', { state: { resumeId: data.id, targetRole } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h2>Upload your resume</h2>
        <p>We'll generate interview questions tailored to your background and target role.</p>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <label>Target role</label>
          <input
            placeholder="e.g. Backend Engineer, Data Analyst"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            required
          />
          <label>Resume file (PDF, DOCX, TXT)</label>
          <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} required />
          <button type="submit" disabled={uploading}>
            {uploading ? 'Uploading…' : 'Continue to interview'}
          </button>
        </form>
      </div>
    </div>
  )
}
