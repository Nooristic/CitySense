import { useState } from "react"
import { askCitySense, predictPm25 } from "../lib/api"
import { pm25Level } from "../lib/aqi"

const SUGGESTED_QUESTIONS = [
  "Which area has the worst air quality right now?",
  "Is it safe to exercise outdoors today?",
]

function AiPanel({ sensors, selectedSensorId }) {
  const [question, setQuestion] = useState("")
  const [chat, setChat] = useState([])
  const [asking, setAsking] = useState(false)
  const [askError, setAskError] = useState(null)

  const [prediction, setPrediction] = useState(null)
  const [predicting, setPredicting] = useState(false)
  const [predictError, setPredictError] = useState(null)

  const selectedSensor = sensors.find((s) => s.sensor_id === selectedSensorId)

  const submitQuestion = async (text) => {
    const trimmed = text.trim()
    if (trimmed.length < 3 || asking) {
      return
    }
    setAsking(true)
    setAskError(null)
    try {
      const data = await askCitySense(trimmed)
      setChat((prev) => [
        ...prev,
        { question: data.question, answer: data.answer, provider: data.provider },
      ])
      setQuestion("")
    } catch (err) {
      setAskError(err.message)
    } finally {
      setAsking(false)
    }
  }

  const runPrediction = async () => {
    if (!selectedSensorId || predicting) {
      return
    }
    setPredicting(true)
    setPredictError(null)
    try {
      setPrediction(await predictPm25(selectedSensorId))
    } catch (err) {
      setPredictError(err.message)
    } finally {
      setPredicting(false)
    }
  }

  return (
    <div className="ai-layout">
      <div className="ai-chat">
        <form
          className="ai-form"
          onSubmit={(event) => {
            event.preventDefault()
            submitQuestion(question)
          }}
        >
          <input
            className="ai-input"
            aria-label="Ask about air quality"
            placeholder="Ask about air quality…"
            value={question}
            maxLength={500}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={asking}
          />
          <button type="submit" disabled={asking || question.trim().length < 3}>
            {asking ? "Thinking…" : "Ask"}
          </button>
        </form>

        <div className="suggest-chips">
          {SUGGESTED_QUESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              disabled={asking}
              onClick={() => submitQuestion(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>

        {askError && <p className="ai-error">{askError}</p>}

        <div className="chat-log">
          {chat.length === 0 && !askError && (
            <p className="empty-state">Answers are grounded in the last 24 h of sensor data.</p>
          )}
          {chat.map((entry, index) => (
            <article key={index} className="chat-entry">
              <p className="chat-question">{entry.question}</p>
              <p className="chat-answer">
                {entry.answer} <span className="provider-badge">{entry.provider}</span>
              </p>
            </article>
          ))}
        </div>
      </div>

      <div className="ai-predict">
        <button
          type="button"
          onClick={runPrediction}
          disabled={!selectedSensorId || predicting}
        >
          {predicting ? "Predicting…" : `Predict PM2.5 · ${selectedSensor?.location ?? "sensor"}`}
        </button>

        {predictError && <p className="ai-error">{predictError}</p>}

        {prediction && !predicting && (
          <div className="prediction-card">
            <p className="prediction-label">Forecast at {prediction.location}</p>
            <p className="prediction-value">
              {prediction.predicted_pm25}{" "}
              <span
                className="chip"
                style={{ backgroundColor: pm25Level(prediction.predicted_pm25).color }}
              >
                {prediction.aqi_category}
              </span>
            </p>
            <p className="prediction-meta">µg/m³ · {prediction.target_time.slice(0, 16).replace("T", " ")}</p>
            <p className="prediction-meta">
              Model: {prediction.model_info.type} · MAE ±{prediction.model_info.mae_pm25} µg/m³ ·{" "}
              {prediction.model_info.trained_on}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AiPanel
