interface Props {
  label: string;
  value: string | number;
  detail: string;
}

export function StatCard({ label, value, detail }: Props) {
  return (
    <div className="stat-card">
      <span className="muted">{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
