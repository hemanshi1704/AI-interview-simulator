import { useEffect, useRef, useState } from 'react'

/**
 * Uses the browser's Web Speech API (SpeechRecognition) to transcribe
 * spoken answers to text in real time. Falls back to a manual textarea
 * if the browser doesn't support it (e.g. Firefox).
 */
export default function VoiceRecorder({ value, onChange }) {
  const [recording, setRecording] = useState(false)
  const [supported, setSupported] = useState(true)
  const recognitionRef = useRef(null)
  const baseTextRef = useRef('')

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setSupported(false)
      return
    }
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let transcript = ''
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      onChange((baseTextRef.current + ' ' + transcript).trim())
    }
    recognition.onerror = () => setRecording(false)
    recognition.onend = () => setRecording(false)

    recognitionRef.current = recognition
    return () => recognition.stop()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startRecording = () => {
    baseTextRef.current = value || ''
    recognitionRef.current?.start()
    setRecording(true)
  }

  const stopRecording = () => {
    recognitionRef.current?.stop()
    setRecording(false)
  }

  return (
    <div>
      <textarea
        rows={5}
        placeholder="Your answer will appear here as you speak, or type it manually."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {supported ? (
        <button
          type="button"
          className={recording ? 'record' : 'secondary'}
          onClick={recording ? stopRecording : startRecording}
        >
          {recording ? '⏹ Stop Recording' : '🎤 Start Voice Answer'}
        </button>
      ) : (
        <p className="error">
          Voice input isn't supported in this browser. Try Chrome/Edge, or type your answer above.
        </p>
      )}
    </div>
  )
}
