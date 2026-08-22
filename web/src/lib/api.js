const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `API ${response.status} on ${path}`)
  }
  return response.json()
}

function post(path, payload) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
}

export const getSensors = () => request("/sensors")

export const getHourlyTrend = (sensorId, hours) =>
  request(`/aggregations/hourly-trend?sensor_id=${encodeURIComponent(sensorId)}&hours=${hours}`)

export const getTopPolluted = (hours, limit = 5) =>
  request(`/aggregations/top-polluted?hours=${hours}&limit=${limit}`)

export const askCitySense = (question) => post("/api/ask", { question })

export const predictPm25 = (sensorId) => post("/api/predict", { sensor_id: sensorId })
