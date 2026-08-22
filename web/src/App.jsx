import { useEffect, useState } from "react"
import SensorMap from "./components/SensorMap"
import HourlyTrend from "./components/HourlyTrend"
import TopPolluted from "./components/TopPolluted"
import { getHourlyTrend, getSensors, getTopPolluted } from "./lib/api"
import { pm25Level } from "./lib/aqi"
import "./App.css"

const HOUR_OPTIONS = [24, 72, 168]

function App() {
  const [sensors, setSensors] = useState([])
  const [selectedSensorId, setSelectedSensorId] = useState(null)
  const [hours, setHours] = useState(72)
  const [trend, setTrend] = useState(null)
  const [topPolluted, setTopPolluted] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSensors()
      .then((data) => {
        setSensors(data)
        if (data.length > 0) {
          setSelectedSensorId(data[0].sensor_id)
        }
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (!selectedSensorId) {
      return undefined
    }
    let cancelled = false
    setLoading(true)
    Promise.all([getHourlyTrend(selectedSensorId, hours), getTopPolluted(hours)])
      .then(([trendData, pollutedData]) => {
        if (cancelled) return
        setTrend(trendData)
        setTopPolluted(pollutedData.top_polluted)
        setError(null)
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [selectedSensorId, hours])

  const latestPoint = trend?.data?.at(-1)
  const selectedLocation = trend?.location ?? selectedSensorId ?? ""

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>
            City<span>Sense</span>
          </h1>
          <p className="subtitle">Hyderabad air quality monitoring</p>
        </div>
        <div className="range-buttons" role="group" aria-label="Time range">
          {HOUR_OPTIONS.map((option) => (
            <button
              key={option}
              type="button"
              className={option === hours ? "active" : ""}
              onClick={() => setHours(option)}
            >
              {option / 24}d
            </button>
          ))}
        </div>
      </header>

      {error && !loading && <div className="error-banner">{error}</div>}

      <main className="grid">
        <section className="panel map-panel">
          <div className="panel-head">
            <h2>Sensor network</h2>
            <span className="hint">Click a marker to inspect it</span>
          </div>
          {sensors.length > 0 ? (
            <SensorMap
              sensors={sensors}
              selectedId={selectedSensorId}
              onSelect={setSelectedSensorId}
            />
          ) : (
            <p className="empty-state">Loading sensors…</p>
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Hourly trends</h2>
            <select
              aria-label="Select sensor"
              value={selectedSensorId ?? ""}
              onChange={(event) => setSelectedSensorId(event.target.value)}
            >
              {sensors.map((sensor) => (
                <option key={sensor.sensor_id} value={sensor.sensor_id}>
                  {sensor.location}
                </option>
              ))}
            </select>
          </div>
          {latestPoint && (
            <p className="chip-row">
              Latest PM2.5 at <strong>{selectedLocation}</strong>{" "}
              <span
                className="chip"
                style={{ backgroundColor: pm25Level(latestPoint.avg_pm25).color }}
              >
                {latestPoint.avg_pm25} µg/m³ · {pm25Level(latestPoint.avg_pm25).label}
              </span>
            </p>
          )}
          <div className="chart-box">
            {loading ? <p className="empty-state">Loading…</p> : <HourlyTrend data={trend?.data ?? []} />}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Most polluted areas</h2>
            <span className="hint">avg PM2.5 · last {hours / 24}d</span>
          </div>
          <div className="chart-box">
            {loading ? (
              <p className="empty-state">Loading…</p>
            ) : (
              <TopPolluted data={topPolluted} />
            )}
          </div>
        </section>

        <section className="panel about-panel">
          <div className="panel-head">
            <h2>About</h2>
          </div>
          <ul className="about-list">
            <li>{sensors.length} sensors across 4 zones</li>
            <li>Readings every 5 minutes (temperature, humidity, PM2.5)</li>
            <li>
              Backend:{" "}
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
                FastAPI docs
              </a>
            </li>
          </ul>
        </section>
      </main>

      <footer className="footer">
        Demo dataset: synthetic readings for Aug 16–22, 2026 · CitySense Day 3
      </footer>
    </div>
  )
}

export default App
