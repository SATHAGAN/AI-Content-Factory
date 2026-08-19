const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

const auth = (token) => ({Authorization: `Bearer ${token}`});

export const api = {
  baseUrl: API_BASE,
  register: (payload) => request("/auth/register", {method: "POST", body: JSON.stringify(payload)}),
  login: (payload) => request("/auth/login", {method: "POST", body: JSON.stringify(payload)}),
  me: (token) => request("/auth/me", {headers: auth(token)}),
  createProject: (payload, token) => request("/workspace/projects", {
    method: "POST", headers: auth(token), body: JSON.stringify(payload),
  }),
  listProjects: (token) => request("/workspace/projects", {headers: auth(token)}),
  enqueueGeneration: (project_id, token) => request("/workspace/generate", {
    method: "POST", headers: auth(token), body: JSON.stringify({project_id}),
  }),
  listJobs: (token) => request("/workspace/jobs", {headers: auth(token)}),
  getJob: (job_id, token) => request(`/workspace/jobs/${job_id}`, {headers: auth(token)}),
  approveJob: (job_id, comment, token) => request(`/workspace/jobs/${job_id}/approve`, {
    method: "POST", headers: auth(token), body: JSON.stringify({comment: comment || null}),
  }),
  rejectJob: (job_id, comment, token) => request(`/workspace/jobs/${job_id}/reject`, {
    method: "POST", headers: auth(token), body: JSON.stringify({comment: comment || null}),
  }),
  artifactBlob: async (job_id, token) => {
    const response = await fetch(`${API_BASE}/workspace/jobs/${job_id}/artifact`, {headers: auth(token)});
    if (!response.ok) throw new Error(`Unable to load video (${response.status})`);
    return response.blob();
  },
};
