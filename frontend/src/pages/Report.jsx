import { useLocation, Link } from 'react-router-dom'
import api from '../api'

export default function Report() {
  const { state } = useLocation()

  const downloadReport = async () => {
    const response = await api.get(`/interview/${state.sessionId}/report`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'interview_feedback_report.pdf')
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  if (!state?.sessionId) {
    return (
      <div className="container">
        <p>No completed interview found. <Link to="/upload">Start a new one</Link>.</p>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="card">
        <h2>Interview complete 🎉</h2>
        <p>Your detailed, question-by-question PDF feedback report is ready.</p>
        <button onClick={downloadReport}>Download PDF Report</button>
      </div>
      <Link to="/upload">Start another interview</Link>
    </div>
  )
}
