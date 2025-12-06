import { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative';
  icon: LucideIcon;
  subtitle?: string;
  featured?: boolean;
  delay?: number;
  loading?: boolean;
}

function MetricCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  subtitle,
  featured = false,
  delay = 0,
  loading = false,
}: MetricCardProps) {
  return (
    <div 
      className={`metric-card ${featured ? 'featured' : ''}`}
      style={{ animation: `fadeInUp 0.5s ease-out ${delay}ms both` }}
    >
      <div className="metric-header">
        <div className="metric-icon">
          <Icon size={20} />
        </div>
        <div className={`metric-change ${changeType}`}>
          {changeType === 'positive' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {change}
        </div>
      </div>
      
      <div className="metric-title">{title}</div>
      <div className="metric-value">
        {loading ? <span className="loading"></span> : value}
      </div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
    </div>
  );
}

export default MetricCard;
