import RecommendationPanel from '../components/RecommendationPanel';
import TopPages from '../components/TopPages';

interface InsightsPageProps {
  recommendations: any[];
  recommendationsLoading: boolean;
}

function InsightsPage({ recommendations, recommendationsLoading }: InsightsPageProps) {
  return (
    <>
      <div className="section-header">
        <h2>💡 Traffic Insights & Recommendations</h2>
        <p>Data-driven actionable recommendations for traffic optimization</p>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">Priority Recommendations</h3>
            <p className="chart-subtitle">Top suggestions based on traffic analysis</p>
          </div>
        </div>
        <RecommendationPanel recommendations={recommendations} loading={recommendationsLoading} />
      </div>

      <div className="content-grid">
        <TopPages recommendations={recommendations} />

        <div className="chart-card">
          <div className="chart-header">
            <div>
              <h3 className="chart-title">Recommendation Summary</h3>
              <p className="chart-subtitle">Key insights</p>
            </div>
          </div>
          <div style={{ padding: '1rem 0' }}>
            <div className="stat-item">
              <div className="stat-label">Total Recommendations</div>
              <div className="stat-value">{recommendations.length}</div>
            </div>
            <div className="stat-item">
              <div className="stat-label">High Priority</div>
              <div className="stat-value">
                {recommendations.filter(r => r.avg_congestion > 2).length}
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Action Items</div>
              <div className="stat-value">
                {recommendations.reduce((sum, r) => sum + r.actions.length, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default InsightsPage;
