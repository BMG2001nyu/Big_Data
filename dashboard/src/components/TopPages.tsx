import { useMemo } from 'react';

interface Recommendation {
  borough: string;
  roadway: string;
  peak_hours: number[];
  avg_congestion: number;
  weekend_ratio: number;
  actions: string[];
}

interface TopPagesProps {
  recommendations: Recommendation[];
}

function TopPages({ recommendations }: TopPagesProps) {
  const topRoads = useMemo(() => {
    return recommendations
      .sort((a, b) => b.avg_congestion - a.avg_congestion)
      .slice(0, 5)
      .map((rec, index) => ({
        rank: index + 1,
        path: `${rec.roadway}`,
        borough: rec.borough,
        views: Math.floor(rec.avg_congestion * 1000),
        change: `+${Math.floor(rec.weekend_ratio * 10)}%`,
        percentage: Math.min(100, Math.floor(rec.avg_congestion * 15)),
      }));
  }, [recommendations]);

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">Top Congested Roads</h3>
          <p className="chart-subtitle">Most congested roads today</p>
        </div>
      </div>

      <div className="pages-list">
        {topRoads.map((page) => (
          <div key={page.rank} className="page-item">
            <div className="page-rank">{page.rank}</div>
            <div className="page-info">
              <div className="page-path">{page.path}</div>
              <div className="page-bar">
                <div 
                  className="page-bar-fill" 
                  style={{ width: `${page.percentage}%` }}
                />
              </div>
            </div>
            <div className="page-stats">
              <div className="page-views">{page.views.toLocaleString()}</div>
              <div className="page-change">{page.change}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TopPages;
