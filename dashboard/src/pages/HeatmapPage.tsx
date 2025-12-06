import HeatmapGrid, { HeatmapPoint } from '../components/HeatmapGrid';

interface HeatmapPageProps {
  heatmapData: HeatmapPoint[];
}

function HeatmapPage({ heatmapData }: HeatmapPageProps) {
  return (
    <>
      <div className="section-header">
        <h2>Traffic Heat Map</h2>
        <p>24-hour traffic intensity by borough</p>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">Peak Hour Heatmap</h3>
            <p className="chart-subtitle">Traffic intensity visualization across all boroughs</p>
          </div>
        </div>
        <HeatmapGrid data={heatmapData} />
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">How to Read the Heatmap</h3>
            <p className="chart-subtitle">Understanding the visualization</p>
          </div>
        </div>
        <div style={{ padding: '1rem 0' }}>
          <div className="heatmap-legend">
            <div className="legend-item-row">
              <div className="legend-color-box" style={{ background: '#1a1f28' }} />
              <div className="legend-text">
                <strong>Low Traffic</strong> - Minimal vehicle activity
              </div>
            </div>
            <div className="legend-item-row">
              <div className="legend-color-box" style={{ background: 'rgba(20, 184, 166, 0.4)' }} />
              <div className="legend-text">
                <strong>Medium Traffic</strong> - Moderate vehicle flow
              </div>
            </div>
            <div className="legend-item-row">
              <div className="legend-color-box" style={{ background: 'rgba(20, 184, 166, 0.8)' }} />
              <div className="legend-text">
                <strong>High Traffic</strong> - Peak congestion periods
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default HeatmapPage;
