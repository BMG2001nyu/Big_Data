interface HeatmapPoint {
  borough: string;
  hour: number;
  value: number;
}

interface HeatmapGridProps {
  data: HeatmapPoint[];
}

function HeatmapGrid({ data }: HeatmapGridProps) {
  if (!data.length) {
    return <div className="empty-state">No live streaming data available.</div>;
  }

  const finiteValues = data.map((point) => point.value).filter((value) => Number.isFinite(value));
  const maxValue = finiteValues.length ? Math.max(...finiteValues, 1) : 1;
  const boroughs = Array.from(new Set(data.map((point) => point.borough))).sort();

  const getValue = (borough: string, hour: number) => {
    const point = data.find((item) => item.borough === borough && item.hour === hour);
    return point ? point.value : 0;
  };

  const getColor = (intensity: number) => {
    if (intensity === 0) return '#1a1f28';
    // Gradient from dark teal to bright teal
    const r = Math.round(20 + intensity * (20 - 20));
    const g = Math.round(184 + intensity * (220 - 184));
    const b = Math.round(166 + intensity * (200 - 166));
    return `rgba(${r}, ${g}, ${b}, ${0.3 + intensity * 0.7})`;
  };

  return (
    <div className="heatmap-container">
      <div className="heatmap-grid-wrapper">
        <div className="heatmap-header">
          <div className="heatmap-corner">Borough</div>
          <div className="heatmap-hours">
            {Array.from({ length: 24 }).map((_, hour) => (
              <div key={hour} className="heatmap-hour-label">{hour}</div>
            ))}
          </div>
        </div>
        {boroughs.map((borough) => (
          <div className="heatmap-row" key={borough}>
            <div className="heatmap-label">{borough}</div>
            <div className="heatmap-cells">
              {Array.from({ length: 24 }).map((_, hour) => {
                const value = getValue(borough, hour);
                const safeValue = Number.isFinite(value) ? value : 0;
                const intensity = Math.max(0, Math.min(1, safeValue / (maxValue || 1)));
                const backgroundColor = getColor(intensity);
                return (
                  <div
                    key={hour}
                    className="heatmap-cell"
                    style={{ 
                      backgroundColor,
                      border: intensity > 0 ? '1px solid rgba(20, 184, 166, 0.3)' : '1px solid #1e293b',
                    }}
                    title={`${borough} @ ${hour}:00 — ${safeValue.toFixed(0)} vehicles`}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export type { HeatmapPoint };
export default HeatmapGrid;

