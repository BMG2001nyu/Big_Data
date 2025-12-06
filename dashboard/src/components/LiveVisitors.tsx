import { useMemo } from 'react';
import { Users } from 'lucide-react';

interface Anomaly {
  requestid: number;
  wktgeom: string;
  direction: string;
  from_hour: string;
  vehicle_count: number;
  duration_minutes: number;
  borough: string;
  roadwayname: string;
}

interface LiveVisitorsProps {
  anomalies: Anomaly[];
}

function LiveVisitors({ anomalies }: LiveVisitorsProps) {
  const liveCount = useMemo(() => {
    return anomalies.slice(0, 10).reduce((sum, a) => sum + a.vehicle_count, 0);
  }, [anomalies]);

  const visitorsByBorough = useMemo(() => {
    const boroughCounts: Record<string, number> = {};
    anomalies.slice(0, 5).forEach((anomaly) => {
      boroughCounts[anomaly.borough] = (boroughCounts[anomaly.borough] || 0) + 1;
    });

    return Object.entries(boroughCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([borough, count]) => ({
        location: borough,
        count,
      }));
  }, [anomalies]);

  return (
    <div className="chart-card">
      <div className="live-header">
        <div>
          <h3 className="chart-title">Live Anomalies</h3>
          <p className="chart-subtitle">Active right now</p>
        </div>
        <div className="live-title-section">
          <div className="live-icon">
            <Users size={20} />
          </div>
          <div>
            <div className="live-count">{liveCount.toLocaleString()}</div>
            <div className="live-label">vehicles detected</div>
          </div>
        </div>
      </div>

      <div className="visitors-list">
        {visitorsByBorough.map((visitor) => (
          <div key={visitor.location} className="visitor-item">
            <div className="visitor-info">
              <div className="visitor-location">{visitor.location}</div>
            </div>
            <div className="visitor-indicator" />
            <div className="visitor-count">{visitor.count}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LiveVisitors;
