import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import KpiCard from './components/KpiCard';
import HeatmapGrid, { HeatmapPoint } from './components/HeatmapGrid';
import RecommendationPanel, { Recommendation } from './components/RecommendationPanel';

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

  const heatmapData: HeatmapPoint[] = useMemo(() => {
    return streamAggregates.map((aggregate) => ({
      borough: aggregate.borough,
      hour: new Date(aggregate.window_start).getHours(),
      value: aggregate.avg_vehicle_count,
    }));
  }, [streamAggregates]);

  const streamChartData = useMemo(() => {
    return streamAggregates.map((aggregate) => ({
      window_end: aggregate.window_end,
      borough: aggregate.borough,
      avg_vehicle_count: aggregate.avg_vehicle_count,
    }));
  }, [streamAggregates]);

  return (
    <div className="layout">
      <header>
        <h1>NYC Traffic Analytics</h1>
        <p>Live and historical insights from NYC automated traffic sensors.</p>
      </header>
      <section className="kpi-grid">
        <KpiCard title="Total Vehicle Volume" value={totalVolume.toLocaleString()} loading={summaryLoading} />
        {boroughKpis.map((item) => (
          <KpiCard key={item.borough} title={`${item.borough} Volume`} value={item.volume.toLocaleString()} loading={summaryLoading} />
        ))}
        <div className={`live-status ${streamConnected ? '' : 'offline'}`}>
          <span className="live-dot" />
          {streamConnected ? 'Live feed connected' : 'Waiting for live feed'}
          {streamLastUpdated && ` • Updated ${streamLastUpdated.toLocaleTimeString()}`}
        </div>
      </section>
      <section>
        <h2>Recent Trends</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={summary}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis dataKey="vehicle_count" />
              <Tooltip />
              <Line type="monotone" dataKey="vehicle_count" stroke="#2563eb" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section>
        <h2>Live Streaming Trends</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={streamChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="window_end" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
              <YAxis />
              <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
              <Legend />
              <Bar dataKey="avg_vehicle_count" name="Avg Vehicle Count" fill="#22d3ee" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section>
        <h2>Peak Hour Heatmap</h2>
        <HeatmapGrid data={heatmapData} />
      </section>
      <section>
        <h2>Latest Anomalies</h2>
        {anomaliesLoading ? (
          <p>Loading...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Borough</th>
                <th>Roadway</th>
                <th>Vehicle Count</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.slice(0, 10).map((anomaly) => (
                <tr key={`${anomaly.from_hour}-${anomaly.roadwayname}`}>
                  <td>{new Date(anomaly.from_hour).toLocaleString()}</td>
                  <td>{anomaly.borough}</td>
                  <td>{anomaly.roadwayname}</td>
                  <td>{anomaly.vehicle_count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      <section>
        <h2>Data-Driven Recommendations</h2>
        <RecommendationPanel recommendations={recommendations.slice(0, 5)} loading={recommendationsLoading} />
      </section>
    </div>
  );
}

export default App;
