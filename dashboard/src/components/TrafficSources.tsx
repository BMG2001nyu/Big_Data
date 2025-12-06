import { useMemo } from 'react';

interface Borough {
  borough: string;
  volume: number;
}

interface TrafficSourcesProps {
  boroughs: Borough[];
}

function TrafficSources({ boroughs }: TrafficSourcesProps) {
  const sources = useMemo(() => {
    const totalVolume = boroughs.reduce((sum, b) => sum + b.volume, 0);
    const colors = ['#14b8a6', '#8b5cf6', '#f97316', '#ec4899', '#06b6d4'];
    
    return boroughs
      .sort((a, b) => b.volume - a.volume)
      .slice(0, 5)
      .map((borough, index) => ({
        name: borough.borough,
        value: borough.volume.toLocaleString(),
        percentage: Math.round((borough.volume / totalVolume) * 100),
        color: colors[index] || colors[0],
      }));
  }, [boroughs]);

  const totalPercentage = useMemo(() => 
    sources.reduce((sum, s) => sum + s.percentage, 0),
    [sources]
  );

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">Traffic Sources</h3>
          <p className="chart-subtitle">Where your vehicles come from</p>
        </div>
      </div>

      <div className="source-bar">
        {sources.map((source) => (
          <div
            key={source.name}
            className="source-bar-segment"
            style={{
              width: `${source.percentage}%`,
              background: source.color,
            }}
          />
        ))}
      </div>

      <div className="source-list">
        {sources.map((source) => (
          <div key={source.name} className="source-item">
            <div className="source-indicator" style={{ background: source.color }} />
            <div className="source-name">{source.name}</div>
            <div className="source-value">{source.value}</div>
            <div className="source-percentage">{source.percentage}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TrafficSources;
