export function Toast({message, error=false}) {
  if (!message) return null;
  return <div className={error ? "toast error" : "toast"}>{message}</div>;
}
