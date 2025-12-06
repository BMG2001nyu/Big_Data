import { Car, AlertTriangle, Clock, MapPin, TrendingUp } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import TrafficChart from '../components/TrafficChart';
import TrafficSources from '../components/TrafficSources';
import TopPages from '../components/TopPages';
import LiveVisitors from '../components/LiveVisitors';

interface OverviewPageProps {
  summary: any[];
  anomalies: any[];
  recommendations: any[];
  streamAggregates: any[];
  summaryLoading: boolean;
  anomaliesLoading: boolean;
  totalVolume: number;
  boroughKpis: any[];
  peakHour: number;
  avgSessionTime: string;
}

function OverviewPage({
  summary,
  anomalies,
  recommendations,
  streamAggregates,
  summaryLoading,
  anomaliesLoading,
  totalVolume,
  boroughKpis,
  peakHour,
  avgSessionTime,
}: OverviewPageProps) {
  const metrics = [
    {
      title: "Total Vehicles",
      value: summaryLoading ? "..." : totalVolume.toLocaleString(),
      change: "+14.2%",
      changeType: "positive" as const,
      icon: Car,
      subtitle: `vs ${Math.floor(totalVolume * 0.88).toLocaleString()} last week`,
      featured: true,
      loading: summaryLoading,
    },
    {
      title: "Anomalies Detected",
      value: anomaliesLoading ? "..." : anomalies.length.toString(),
      change: "+8.7%",
      changeType: "positive" as const,
      icon: AlertTriangle,
      subtitle: "Unusual traffic patterns",
      loading: anomaliesLoading,
    },
    {
      title: "Peak Traffic Hour",
      value: summaryLoading ? "..." : `${peakHour}:00`,
      change: "-4.1%",
      changeType: "positive" as const,
      icon: Clock,
      subtitle: "Highest volume time",
      loading: summaryLoading,
    },
    {
      title: "Avg. Session",
      value: summaryLoading ? "..." : avgSessionTime,
      change: "+12.3%",
      changeType: "positive" as const,
      icon: TrendingUp,
      loading: summaryLoading,
    },
  ];

  const boroughMetrics = boroughKpis.slice(0, 5).map((kpi) => ({
    title: kpi.borough,
    value: summaryLoading ? "..." : kpi.volume.toLocaleString(),
    change: "+8.2%",
    changeType: "positive" as const,
    icon: MapPin,
    subtitle: "vehicles tracked",
    loading: summaryLoading,
  }));

  return (
    <>
      <div className="section-header">
        <h2>Overview</h2>
        <p>Key metrics and performance indicators</p>
      </div>

      <div className="metrics-grid">
        {metrics.map((metric, index) => (
          <MetricCard key={metric.title} {...metric} delay={index * 50} />
        ))}
      </div>

      <div className="section-header">
        <h2>Borough Overview</h2>
        <p>Traffic volume by region</p>
      </div>
      <div className="metrics-grid">
        {boroughMetrics.map((metric, index) => (
          <MetricCard key={metric.title} {...metric} delay={index * 50} />
        ))}
      </div>

      <div className="content-grid">
        <TrafficChart data={summary} streamData={streamAggregates} />
        <TrafficSources boroughs={boroughKpis} />
      </div>

      <div className="bottom-grid">
        <TopPages recommendations={recommendations} />
        <LiveVisitors anomalies={anomalies} />
      </div>
    </>
  );
}

export default OverviewPage;
