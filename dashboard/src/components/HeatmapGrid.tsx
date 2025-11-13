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
    return <p className="empty-state">No live streaming data available.</p>;
  }

  const finiteValues = data.map((point) => point.value).filter((value) => Number.isFinite(value));
  const maxValue = finiteValues.length ? Math.max(...finiteValues, 1) : 1;
  const boroughs = Array.from(new Set(data.map((point) => point.borough))).sort();

  const getValue = (borough: string, hour: number) => {
    const point = data.find((item) => item.borough === borough && item.hour === hour);
    return point ? point.value : 0;
  };

  return (
    <div className="heatmap-grid">
      <div className="heatmap-header">
        <span>Borough</span>
        <div className="heatmap-hours">
          {Array.from({ length: 24 }).map((_, hour) => (
            <span key={hour}>{hour}</span>
          ))}
        </div>
      </div>
      {boroughs.map((borough) => (
        <div className="heatmap-row" key={borough}>
          <span className="heatmap-label">{borough}</span>
          <div className="heatmap-cells">
            {Array.from({ length: 24 }).map((_, hour) => {
              const value = getValue(borough, hour);
              const safeValue = Number.isFinite(value) ? value : 0;
              const intensity = Math.max(0, Math.min(1, safeValue / (maxValue || 1)));
              const backgroundColor = `rgba(37, 99, 235, ${intensity.toFixed(2)})`;
              return (
                <div
                  key={hour}
                  className="heatmap-cell"
                  style={{ backgroundColor }}
                  title={`${borough} @ ${hour}:00 — ${safeValue.toFixed(0)} vehicles`}
                />
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export type { HeatmapPoint };
export default HeatmapGrid;

