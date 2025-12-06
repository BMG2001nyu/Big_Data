import TrafficChart from '../components/TrafficChart';
import TrafficSources from '../components/TrafficSources';

interface AnalyticsPageProps {
  summary: any[];
  streamAggregates: any[];
  boroughKpis: any[];
}

function AnalyticsPage({ summary, streamAggregates, boroughKpis }: AnalyticsPageProps) {
  return (
    <>
      <div className="section-header">
        <h2>Analytics</h2>
        <p>Detailed traffic analysis and trends</p>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">Traffic Volume Over Time</h3>
            <p className="chart-subtitle">Historical trends and patterns</p>
          </div>
        </div>
        <TrafficChart data={summary} streamData={streamAggregates} />
      </div>

      <div className="content-grid">
        <div className="chart-card">
          <div className="chart-header">
            <div>
              <h3 className="chart-title">Borough Distribution</h3>
              <p className="chart-subtitle">Traffic breakdown by region</p>
            </div>
          </div>
          <TrafficSources boroughs={boroughKpis} />
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <div>
              <h3 className="chart-title">Key Statistics</h3>
              <p className="chart-subtitle">Quick insights</p>
            </div>
          </div>
          <div style={{ padding: '2rem' }}>
            <div className="stat-item">
              <div className="stat-label">Total Boroughs</div>
              <div className="stat-value">{boroughKpis.length}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Data Points</div>
              <div className="stat-value">{summary.length.toLocaleString()}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Total Volume</div>
              <div className="stat-value">
                {boroughKpis.reduce((sum, b) => sum + b.volume, 0).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default AnalyticsPage;
