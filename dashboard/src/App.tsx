import { useQuery } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import Navigation from './components/Navigation';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import AnalyticsPage from './pages/AnalyticsPage';
import HeatmapPage from './pages/HeatmapPage';
import AnomaliesPage from './pages/AnomaliesPage';
import InsightsPage from './pages/InsightsPage';
import { HeatmapPoint } from './components/HeatmapGrid';

interface TrafficSummary {
  date: string;
  borough: string;
  vehicle_count: number;
}

interface AnomalyRecord {
  from_hour: string;
  borough: string;
  roadwayname: string;
  vehicle_count: number;
}

interface StreamAggregate {
  window_start: string;
  window_end: string;
  borough: string;
  roadwayname: string;
  avg_vehicle_count: number;
}

interface RecommendationResponse extends Recommendation {}

const apiBaseUrl = import.meta.env.VITE_API_URL ?? '/api';
const wsBaseUrl = import.meta.env.VITE_API_WS_URL;

const apiClient = axios.create({
  baseURL: apiBaseUrl,
});

const fetchTrafficSummary = async () => {
  const { data } = await apiClient.get<TrafficSummary[]>('/traffic/summary');
  return data;
};

const fetchAnomalies = async () => {
  const { data } = await apiClient.get<AnomalyRecord[]>('/traffic/anomalies');
  return data;
};

const fetchStreamAggregates = async () => {
  const { data } = await apiClient.get<StreamAggregate[]>('/traffic/stream/aggregates');
  return data;
};

const fetchRecommendations = async () => {
  const { data } = await apiClient.get<RecommendationResponse[]>('/traffic/recommendations');
  return data;
};

function App() {
  const { data: summary = [], isLoading: summaryLoading } = useQuery({
    queryKey: ['traffic-summary'],
    queryFn: fetchTrafficSummary,
  });
  const { data: anomalies = [], isLoading: anomaliesLoading } = useQuery({
    queryKey: ['traffic-anomalies'],
    queryFn: fetchAnomalies,
  });
  const { data: streamAggregatesInitial = [] } = useQuery({
    queryKey: ['traffic-stream-aggregates'],
    queryFn: fetchStreamAggregates,
  });
  const { data: recommendations = [], isLoading: recommendationsLoading } = useQuery({
    queryKey: ['traffic-recommendations'],
    queryFn: fetchRecommendations,
  });

  const [streamAggregates, setStreamAggregates] = useState<StreamAggregate[]>(streamAggregatesInitial);
  const [streamConnected, setStreamConnected] = useState(false);
  const [streamLastUpdated, setStreamLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    setStreamAggregates(streamAggregatesInitial);
  }, [streamAggregatesInitial]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const defaultWsUrl = `${protocol}//${window.location.host}/ws/traffic`;
    const websocket = new WebSocket(wsBaseUrl ?? defaultWsUrl);

    websocket.onopen = () => {
      setStreamConnected(true);
    };

    websocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'stream_update') {
          setStreamAggregates(payload.data ?? []);
          setStreamLastUpdated(new Date());
        }
      } catch (error) {
        console.error('Failed to parse stream payload', error);
      }
    };

    websocket.onclose = () => {
      setStreamConnected(false);
    };

    return () => websocket.close();
  }, []);

  const totalVolume = useMemo(
    () => summary.reduce((acc, row) => acc + row.vehicle_count, 0),
    [summary],
  );

  const boroughKpis = useMemo(() => {
    const grouped: Record<string, number> = {};
    summary.forEach((row) => {
      grouped[row.borough] = (grouped[row.borough] ?? 0) + row.vehicle_count;
    });
    return Object.entries(grouped).map(([borough, volume]) => ({ borough, volume }));
  }, [summary]);

  const avgSessionTime = useMemo(() => {
    if (summary.length === 0) return '4m 28s';
    const avgMinutes = Math.floor(summary.length / 60);
    const avgSeconds = summary.length % 60;
    return `${avgMinutes}m ${avgSeconds}s`;
  }, [summary]);

  const peakHour = useMemo(() => {
    if (summary.length === 0) return 0;
    const hourCounts: Record<number, number> = {};
    summary.forEach((row) => {
      const hour = new Date(row.date).getHours();
      hourCounts[hour] = (hourCounts[hour] || 0) + row.vehicle_count;
    });
    const peak = Object.entries(hourCounts).sort((a, b) => b[1] - a[1])[0];
    return peak ? parseInt(peak[0]) : 0;
  }, [summary]);

  const heatmapData: HeatmapPoint[] = useMemo(() => {
    return streamAggregates.map((aggregate) => ({
      borough: aggregate.borough,
      hour: new Date(aggregate.window_start).getHours(),
      value: aggregate.avg_vehicle_count,
    }));
  }, [streamAggregates]);

  return (
    <Router>
      <div className="dashboard-container">
        <div className="dashboard-background">
          <div className="dashboard-background-orb-1" />
          <div className="dashboard-background-orb-2" />
          <div className="dashboard-background-orb-3" />
          <div className="dashboard-background-grid" />
        </div>
        
        <Navigation />
        
        <div className="dashboard-content">
          <Header 
            connected={streamConnected}
            lastUpdated={streamLastUpdated}
            boroughs={boroughKpis.length}
            peakTraffic={`${peakHour}:00`}
          />
          
          <Routes>
            <Route 
              path="/" 
              element={
                <OverviewPage
                  summary={summary}
                  anomalies={anomalies}
                  recommendations={recommendations}
                  streamAggregates={streamAggregates}
                  summaryLoading={summaryLoading}
                  anomaliesLoading={anomaliesLoading}
                  totalVolume={totalVolume}
                  boroughKpis={boroughKpis}
                  peakHour={peakHour}
                  avgSessionTime={avgSessionTime}
                />
              } 
            />
            <Route 
              path="/analytics" 
              element={
                <AnalyticsPage
                  summary={summary}
                  streamAggregates={streamAggregates}
                  boroughKpis={boroughKpis}
                />
              } 
            />
            <Route 
              path="/heatmap" 
              element={
                <HeatmapPage heatmapData={heatmapData} />
              } 
            />
            <Route 
              path="/anomalies" 
              element={
                <AnomaliesPage
                  anomalies={anomalies}
                  anomaliesLoading={anomaliesLoading}
                />
              } 
            />
            <Route 
              path="/insights" 
              element={
                <InsightsPage
                  recommendations={recommendations}
                  recommendationsLoading={recommendationsLoading}
                />
              } 
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
