import { Activity, TrendingUp } from 'lucide-react';

interface HeaderProps {
  connected: boolean;
  lastUpdated: Date | null;
  boroughs: number;
  peakTraffic: string;
}

function Header({ connected, lastUpdated, boroughs, peakTraffic }: HeaderProps) {
  return (
    <div className="header">
      <div className="header-left">
        <div className="header-icon">
          <Activity size={28} strokeWidth={2.5} />
        </div>
        <div className="header-title">
          <h1>NYC Traffic Analytics</h1>
          <p>Real-time insights from automated sensors</p>
        </div>
      </div>
      
      <div className="header-right">
        <div className={`status-badge ${connected ? '' : 'offline'}`}>
          <span className="status-dot" />
          {connected ? 'Live' : 'Connecting'}
        </div>
        <div className="header-stat">
          🌐 {boroughs} boroughs
        </div>
        <div className="header-stat">
          ⚡ Peak: {peakTraffic}
        </div>
      </div>
    </div>
  );
}

export default Header;
