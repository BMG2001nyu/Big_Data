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
    return <p className="empty-state">Loading recommendations...</p>;
  }

  if (!recommendations.length) {
    return <p className="empty-state">No recommendations generated yet.</p>;
  }

  return (
    <div className="recommendation-panel">
      {recommendations.map((item) => (
        <div key={`${item.borough}-${item.roadway}`} className="recommendation-item">
          <h3>
            {item.borough} — {item.roadway}
          </h3>
          <p>
            Peak hours: {item.peak_hours.join(', ')} | Avg congestion: {item.avg_congestion}{' '}
            | Weekend ratio: {item.weekend_ratio}
          </p>
          <ul>
            {item.actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export type { Recommendation };
export default RecommendationPanel;

