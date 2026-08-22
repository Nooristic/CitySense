export function pm25Level(pm25) {
  if (pm25 <= 50) return { label: "Good", color: "#22c55e" }
  if (pm25 <= 100) return { label: "Moderate", color: "#facc15" }
  if (pm25 <= 150) return { label: "Poor", color: "#f97316" }
  if (pm25 <= 200) return { label: "Very Poor", color: "#ef4444" }
  return { label: "Severe", color: "#7f1d1d" }
}
