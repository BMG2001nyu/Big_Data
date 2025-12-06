interface Props {
  title: string;
  value: string;
  loading?: boolean;
}

function KpiCard({ title, value, loading = false }: Props) {
  return (
    <div className="kpi-card">
      <h3>{title}</h3>
      <p>{loading ? <span className="loading"></span> : value}</p>
    </div>
  );
}

export default KpiCard;
