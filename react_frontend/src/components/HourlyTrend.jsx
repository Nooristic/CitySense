import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js"
import { Line } from "react-chartjs-2"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const TICK_COLOR = "#94a3b8"
const GRID_COLOR = "rgba(148, 163, 184, 0.12)"

function formatHour(iso) {
  return new Date(iso).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    hour12: true,
  })
}

function HourlyTrend({ data }) {
  if (!data || data.length === 0) {
    return <p className="empty-state">No readings in this time window.</p>
  }

  const labels = data.map((row) => formatHour(row.hour))
  const chartData = {
    labels,
    datasets: [
      {
        label: "PM2.5 (µg/m³)",
        data: data.map((row) => row.avg_pm25),
        borderColor: "#ef4444",
        backgroundColor: "#ef4444",
        yAxisID: "y1",
        pointRadius: 2,
        tension: 0.3,
      },
      {
        label: "Temperature (°C)",
        data: data.map((row) => row.avg_temperature),
        borderColor: "#f97316",
        backgroundColor: "#f97316",
        yAxisID: "y",
        pointRadius: 2,
        tension: 0.3,
      },
      {
        label: "Humidity (%)",
        data: data.map((row) => row.avg_humidity),
        borderColor: "#38bdf8",
        backgroundColor: "#38bdf8",
        yAxisID: "y",
        pointRadius: 2,
        tension: 0.3,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { legend: { labels: { color: TICK_COLOR } } },
    scales: {
      x: {
        ticks: { color: TICK_COLOR, maxTicksLimit: 10 },
        grid: { color: GRID_COLOR },
      },
      y: {
        position: "left",
        title: { display: true, text: "°C / %", color: TICK_COLOR },
        ticks: { color: TICK_COLOR },
        grid: { color: GRID_COLOR },
      },
      y1: {
        position: "right",
        title: { display: true, text: "µg/m³", color: TICK_COLOR },
        ticks: { color: TICK_COLOR },
        grid: { drawOnChartArea: false },
      },
    },
  }

  return <Line data={chartData} options={options} />
}

export default HourlyTrend
