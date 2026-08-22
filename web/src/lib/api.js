const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`API ${response.status} on ${path}`)
  }
  return response.json()
}

export const getSensors = () => request("/sensors")

export const getHourlyTrend = (sensorId, hours) =>
  request(`/aggregations/hourly-trend?sensor_id=${encodeURIComponent(sensorId)}&hours=${hours}`)

export const getTopPolluted = (hours, limit = 5) =>
  request(`/aggregations/top-polluted?hours=${hours}&limit=${limit}`)
