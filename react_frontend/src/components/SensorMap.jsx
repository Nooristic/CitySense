import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet"
import "leaflet/dist/leaflet.css"

const ZONE_COLORS = {
  "Zone A": "#3b82f6",
  "Zone B": "#8b5cf6",
  "Zone C": "#14b8a6",
  "Zone D": "#f59e0b",
}

function SensorMap({ sensors, selectedId, onSelect }) {
  return (
    <MapContainer center={[17.42, 78.44]} zoom={11} className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {sensors.map((sensor) => {
        const isSelected = sensor.sensor_id === selectedId
        const color = ZONE_COLORS[sensor.zone] ?? "#3b82f6"
        return (
          <CircleMarker
            key={sensor.sensor_id}
            center={[sensor.latitude, sensor.longitude]}
            radius={isSelected ? 13 : 8}
            pathOptions={{
              color: isSelected ? "#ffffff" : color,
              fillColor: color,
              fillOpacity: 0.85,
              weight: isSelected ? 3 : 1.5,
            }}
            eventHandlers={{ click: () => onSelect(sensor.sensor_id) }}
          >
            <Popup>
              <strong>{sensor.name}</strong>
              <br />
              {sensor.location} ({sensor.zone})
              <br />
              Status: {sensor.status}
            </Popup>
          </CircleMarker>
        )
      })}
    </MapContainer>
  )
}

export default SensorMap
