import AnomalyTable from '../components/AnomalyTable';
import LiveVisitors from '../components/LiveVisitors';

interface AnomaliesPageProps {
  anomalies: any[];
  anomaliesLoading: boolean;
}

function AnomaliesPage({ anomalies, anomaliesLoading }: AnomaliesPageProps) {
  return (
    <>
      <div className="section-header">
        <h2>⚠️ Traffic Anomalies</h2>
        <p>Unusual patterns and events requiring attention</p>
      </div>

      <div className="content-grid">
        <div className="chart-card" style={{ gridColumn: 'span 2' }}>
          <div className="chart-header">
            <div>
              <h3 className="chart-title">Latest Anomalies Detected</h3>
              <p className="chart-subtitle">Real-time anomaly detection results</p>
            </div>
          </div>
          <AnomalyTable anomalies={anomalies} loading={anomaliesLoading} />
        </div>
      </div>

      <div className="content-grid">
        <div className="chart-card">
          <LiveVisitors anomalies={anomalies} />
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <div>
              <h3 className="chart-title">Anomaly Statistics</h3>
              <p className="chart-subtitle">Detection summary</p>
            </div>
          </div>
          <div style={{ padding: '1rem 0' }}>
            <div className="stat-item">
              <div className="stat-label">Total Detected</div>
              <div className="stat-value">{anomalies.length}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Unique Boroughs</div>
              <div className="stat-value">
                {new Set(anomalies.map(a => a.borough)).size}
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Avg Severity</div>
              <div className="stat-value">
                {anomalies.length > 0
                  ? ((anomalies.reduce((sum, a) => sum + (a.anomaly_severity || 0), 0) / anomalies.length) * 100).toFixed(2)
                  : '0'}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default AnomaliesPage;
