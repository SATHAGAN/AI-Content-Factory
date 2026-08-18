const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { detail = (await response.json()).detail || detail; } catch {}
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  createProject: (payload, token) => request("/workspace/projects", {
    method: "POST", headers: {Authorization: `Bearer ${token}`}, body: JSON.stringify(payload)
  }),
  enqueueGeneration: (project_id, token) => request("/workspace/generate", {
    method: "POST", headers: {Authorization: `Bearer ${token}`}, body: JSON.stringify({project_id})
  }),
  listJobs: (token) => request("/workspace/jobs", {headers:{Authorization:`Bearer ${token}`}}),
  getJob: (job_id, token) => request(`/workspace/jobs/${job_id}`, {headers:{Authorization:`Bearer ${token}`}}),
};
