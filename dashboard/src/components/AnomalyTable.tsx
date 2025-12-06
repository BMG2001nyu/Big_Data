interface Anomaly {
  requestid: number;
  wktgeom: string;
  direction: string;
  from_hour: string;
  vehicle_count: number;
  duration_minutes: number;
  borough: string;
  roadwayname: string;
  segment_id?: number;
  from_street?: string;
  to_street?: string;
  anomaly_score?: number;
  anomaly_severity?: number;
}

interface AnomalyTableProps {
  anomalies: Anomaly[];
  loading?: boolean;
}

function AnomalyTable({ anomalies, loading = false }: AnomalyTableProps) {
  if (loading) {
    return (
      <div className="empty-state">
        <span className="loading"></span> Loading anomalies...
      </div>
    );
  }

  if (anomalies.length === 0) {
    return <div className="empty-state">No anomalies detected</div>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Borough</th>
            <th>Roadway</th>
            <th>Direction</th>
            <th>Vehicle Count</th>
            <th>Severity</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.slice(0, 15).map((anomaly, index) => (
            <tr key={`${anomaly.from_hour}-${anomaly.roadwayname}-${index}`}>
              <td className="timestamp-cell">
                {new Date(anomaly.from_hour).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </td>
              <td>
                <span className="borough-badge">
                  {anomaly.borough}
                </span>
              </td>
              <td className="roadway-cell">{anomaly.roadwayname}</td>
              <td>
                <span className="direction-badge">{anomaly.direction || 'N/A'}</span>
              </td>
              <td className="count-cell">{anomaly.vehicle_count.toLocaleString()}</td>
              <td>
                <div className="severity-indicator">
                  <div 
                    className="severity-bar"
                    style={{ 
                      width: `${Math.min(100, (anomaly.anomaly_severity || 0) * 1000)}%` 
                    }}
                  />
                  <span className="severity-text">
                    {((anomaly.anomaly_severity || 0) * 100).toFixed(2)}%
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AnomalyTable;
