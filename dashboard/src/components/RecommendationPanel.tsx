interface Recommendation {
  borough: string;
  roadway: string;
  peak_hours: number[];
  avg_congestion: number;
  weekend_ratio: number;
  actions: string[];
}

interface RecommendationPanelProps {
  recommendations: Recommendation[];
  loading?: boolean;
}

function RecommendationPanel({ recommendations, loading = false }: RecommendationPanelProps) {
  if (loading) {
    return (
      <div className="empty-state">
        <span className="loading"></span> Loading recommendations...
      </div>
    );
  }

  if (!recommendations.length) {
    return <div className="empty-state">No recommendations generated yet.</div>;
  }

  return (
    <div className="recommendation-grid">
      {recommendations.slice(0, 6).map((item, index) => (
        <div 
          key={`${item.borough}-${item.roadway}-${index}`} 
          className="recommendation-card"
          style={{ animation: `fadeInUp 0.5s ease-out ${index * 100}ms both` }}
        >
          <div className="recommendation-header">
            <div className="recommendation-priority">
              Priority {index + 1}
            </div>
          </div>
          
          <h4 className="recommendation-title">
            {item.roadway}
          </h4>
          <div className="recommendation-location">{item.borough}</div>
          
          <div className="recommendation-metrics">
            <div className="metric-item">
              <span className="metric-label">Peak Hours</span>
              <span className="metric-value">{item.peak_hours.slice(0, 3).join(', ')}:00</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Congestion</span>
              <span className="metric-value">{item.avg_congestion.toFixed(2)}x</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Weekend Ratio</span>
              <span className="metric-value">{item.weekend_ratio.toFixed(2)}x</span>
            </div>
          </div>
          
          <div className="recommendation-actions">
            <div className="actions-header">Recommended Actions:</div>
            <ul>
              {item.actions.map((action, actionIndex) => (
                <li key={`${action}-${actionIndex}`}>{action}</li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}

export type { Recommendation };
export default RecommendationPanel;

