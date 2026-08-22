import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js"
import { Bar } from "react-chartjs-2"
import { pm25Level } from "../lib/aqi"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const TICK_COLOR = "#94a3b8"
const GRID_COLOR = "rgba(148, 163, 184, 0.12)"

function TopPolluted({ data }) {
  if (!data || data.length === 0) {
    return <p className="empty-state">No readings in this time window.</p>
  }

  const chartData = {
    labels: data.map((row) => row.location),
    datasets: [
      {
        label: "Avg PM2.5 (µg/m³)",
        data: data.map((row) => row.avg_pm25),
        backgroundColor: data.map((row) => pm25Level(row.avg_pm25).color),
        borderRadius: 6,
      },
    ],
  }

  const options = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: {
        title: { display: true, text: "µg/m³", color: TICK_COLOR },
        ticks: { color: TICK_COLOR },
        grid: { color: GRID_COLOR },
      },
      y: { ticks: { color: TICK_COLOR }, grid: { display: false } },
    },
  }

  return <Bar data={chartData} options={options} />
}

export default TopPolluted
