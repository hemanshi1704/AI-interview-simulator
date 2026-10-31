import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../api'
import VoiceRecorder from '../components/VoiceRecorder'
import ScoreCard from '../components/ScoreCard'

export default function Interview() {
  const { state } = useLocation()
  const navigate = useNavigate()

  const [sessionId, setSessionId] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [lastResult, setLastResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!state?.targetRole) {
      navigate('/upload')
      return
    }
    const start = async () => {
      try {
        const { data } = await api.post('/interview/start', {
          resume_id: state.resumeId,
          target_role: state.targetRole,
          num_questions: 5,
        })
        setSessionId(data.session_id)
        setQuestions(data.questions)
      } catch (err) {
        setError(err.response?.data?.detail || 'Could not start interview')
      } finally {
        setLoading(false)
      }
    }
    start()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const currentQuestion = questions[currentIndex]

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return setError('Please provide an answer before submitting.')
    setSubmitting(true)
    setError('')
    try {
      const { data } = await api.post('/interview/answer', {
        question_id: currentQuestion.id,
        answer_text: answer,
      })
      setLastResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Evaluation failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    setAnswer('')
    setLastResult(null)
    if (currentIndex + 1 < questions.length) {
      setCurrentIndex(currentIndex + 1)
    } else {
      finishInterview()
    }
  }

  const finishInterview = async () => {
    try {
      await api.post(`/interview/${sessionId}/complete`)
      navigate('/report', { state: { sessionId } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not complete interview')
    }
  }

  if (loading) return <div className="container"><p>Generating your interview questions…</p></div>
  if (!currentQuestion) return <div className="container"><p>No questions available.</p></div>

  return (
    <div className="container">
      <div className="card">
        <p>Question {currentIndex + 1} of {questions.length} · <em>{currentQuestion.category}</em></p>
        <h3>{currentQuestion.question_text}</h3>

        {error && <p className="error">{error}</p>}

        {!lastResult ? (
          <>
            <VoiceRecorder value={answer} onChange={setAnswer} />
            <button onClick={handleSubmitAnswer} disabled={submitting}>
              {submitting ? 'Evaluating…' : 'Submit Answer'}
            </button>
          </>
        ) : (
          <>
            <ScoreCard technical={lastResult.technical_score} communication={lastResult.communication_score} />
            <p>{lastResult.feedback}</p>
            <button onClick={handleNext}>
              {currentIndex + 1 < questions.length ? 'Next Question' : 'Finish Interview'}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
