import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface TrafficData {
  date: string;
  borough: string;
  vehicle_count: number;
}

interface StreamData {
  window_start: string;
  window_end: string;
  borough: string;
  roadwayname: string;
  avg_vehicle_count: number;
}

interface TrafficChartProps {
  data: TrafficData[];
  streamData: StreamData[];
}

function TrafficChart({ data, streamData }: TrafficChartProps) {
  const chartData = useMemo(() => {
    const grouped: Record<string, { date: string; visitors: number; pageviews: number }> = {};
    
    data.forEach((row) => {
      if (!grouped[row.date]) {
        grouped[row.date] = { date: row.date, visitors: 0, pageviews: 0 };
      }
      grouped[row.date].visitors += row.vehicle_count;
      grouped[row.date].pageviews += Math.floor(row.vehicle_count * 1.5);
    });
    
    return Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date));
  }, [data]);

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">Traffic Overview</h3>
          <p className="chart-subtitle">Today's visitor activity</p>
        </div>
        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#14b8a6' }} />
            <span>Vehicles</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#8b5cf6' }} />
            <span>Observations</span>
          </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorVisitors" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorPageviews" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis 
            dataKey="date" 
            stroke="#64748b" 
            style={{ fontSize: '0.75rem' }}
            tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          />
          <YAxis stroke="#64748b" style={{ fontSize: '0.75rem' }} />
          <Tooltip
            contentStyle={{
              background: '#1a1f28',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              color: '#f8fafc',
            }}
          />
          <Area
            type="monotone"
            dataKey="visitors"
            stroke="#14b8a6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorVisitors)"
          />
          <Area
            type="monotone"
            dataKey="pageviews"
            stroke="#8b5cf6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorPageviews)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrafficChart;
