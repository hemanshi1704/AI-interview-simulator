export default function ScoreCard({ technical, communication }) {
  return (
    <div>
      <span className="score-badge">Technical: {technical?.toFixed(1)} / 10</span>
      <span className="score-badge">Communication: {communication?.toFixed(1)} / 10</span>
    </div>
  )
}
