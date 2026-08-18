import { useEffect, useMemo, useState } from "react";
import { api } from "./lib/api";
import type { Channel, ContentProfile, Project } from "./types";
import { StatCard } from "./components/StatCard";

type Tab = "dashboard" | "create" | "projects" | "channels" | "profiles";

export function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("acf_token")));
  const [channels, setChannels] = useState<Channel[]>([]);
  const [profiles, setProfiles] = useState<ContentProfile[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState("");

  async function refresh() {
    if (!localStorage.getItem("acf_token")) return;
    try {
      setError("");
      const [c, p, pr] = await Promise.all([api.channels(), api.profiles(), api.projects()]);
      setChannels(c);
      setProfiles(p);
      setProjects(pr);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load data");
    }
  }

  useEffect(() => {
    void refresh();
  }, [authenticated]);

  if (!authenticated) {
    return <Auth onAuthenticated={() => setAuthenticated(true)} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">AI Content Factory</div>
        <div className="nav">
          {(["dashboard", "create", "projects", "channels", "profiles"] as Tab[]).map((item) => (
            <button className={tab === item ? "nav-item active" : "nav-item"} key={item} onClick={() => setTab(item)}>
              {item[0].toUpperCase() + item.slice(1)}
            </button>
          ))}
        </div>
        <button
          className="logout"
          onClick={() => {
            localStorage.removeItem("acf_token");
            setAuthenticated(false);
          }}
        >
          Sign out
        </button>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">CONTROL CENTER</p>
            <h1>{tab === "dashboard" ? "Content overview" : tab[0].toUpperCase() + tab.slice(1)}</h1>
          </div>
          <div className="status-dot">API connected</div>
        </header>

        {error && <div className="error">{error}</div>}

        {tab === "dashboard" && (
          <>
            <section className="stats">
              <StatCard label="Channels" value={channels.length} detail="Connected channel profiles" />
              <StatCard label="Content profiles" value={profiles.length} detail="Dynamic content recipes" />
              <StatCard label="Projects" value={projects.length} detail="Projects in workspace" />
              <StatCard label="Automation" value="Manual" detail="Approval mode can change later" />
            </section>

            <section className="hero">
              <div>
                <p className="eyebrow">NEXT GENERATION PIPELINE</p>
                <h2>Turn an idea or transcript into a production-ready video.</h2>
                <p className="muted">
                  Phase 2 establishes the control surface. AI generation workers will plug into this workflow in later phases.
                </p>
                <button className="primary" onClick={() => setTab("create")}>Create a project</button>
              </div>
              <div className="pipeline">
                {["Source", "Script", "Scenes", "Voice", "Render", "QA", "Publish"].map((step, i) => (
                  <div className="pipeline-step" key={step}>
                    <span>{String(i + 1).padStart(2, "0")}</span>
                    {step}
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {tab === "create" && (
          <CreateProject channels={channels} profiles={profiles} onCreated={async () => { await refresh(); setTab("projects"); }} />
        )}

        {tab === "projects" && (
          <section className="panel">
            <div className="panel-head">
              <div>
                <p className="eyebrow">WORKSPACE</p>
                <h2>Projects</h2>
              </div>
              <button className="primary" onClick={() => setTab("create")}>New project</button>
            </div>
            {projects.length === 0 ? (
              <div className="empty">No projects yet. Create your first content project.</div>
            ) : (
              <div className="project-list">
                {projects.map((project) => (
                  <div className="project-row" key={project.id}>
                    <div>
                      <strong>{project.name}</strong>
                      <span className="muted">{project.status}</span>
                    </div>
                    <span className="pill">{String(project.settings.video_type ?? "draft")}</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {tab === "channels" && (
          <section className="panel">
            <p className="eyebrow">MULTI-CHANNEL</p>
            <h2>Channels</h2>
            <div className="grid-list">
              {channels.map((channel) => (
                <div className="mini-card" key={channel.id}>
                  <strong>{channel.name}</strong>
                  <span>{channel.default_language.toUpperCase()}</span>
                  <small>{channel.daily_shorts_target} Shorts · {channel.daily_long_target} long/day</small>
                </div>
              ))}
              {!channels.length && <div className="empty">Create a channel through the API for now; channel creation UI is planned for the next dashboard iteration.</div>}
            </div>
          </section>
        )}

        {tab === "profiles" && (
          <section className="panel">
            <p className="eyebrow">DYNAMIC CONTENT</p>
            <h2>Content profiles</h2>
            <div className="grid-list">
              {profiles.map((profile) => (
                <div className="mini-card" key={profile.id}>
                  <strong>{profile.name}</strong>
                  <span>{profile.category}</span>
                  <small>{profile.language} · {profile.tone ?? "Default tone"}</small>
                </div>
              ))}
              {!profiles.length && <div className="empty">No profiles yet.</div>}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function Auth({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organization, setOrganization] = useState("My Content Studio");
  const [error, setError] = useState("");

  async function submit() {
    try {
      setError("");
      const result = mode === "register"
        ? await api.register(email, password, organization)
        : await api.login(email, password);
      localStorage.setItem("acf_token", result.access_token);
      onAuthenticated();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Authentication failed");
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">AI CONTENT FACTORY</p>
        <h1>{mode === "register" ? "Create your workspace" : "Welcome back"}</h1>
        <p className="muted">A configurable home for your AI content pipeline.</p>
        {mode === "register" && (
          <input value={organization} onChange={(e) => setOrganization(e.target.value)} placeholder="Workspace name" />
        )}
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" type="email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
        {error && <div className="error">{error}</div>}
        <button className="primary full" onClick={() => void submit()}>{mode === "register" ? "Create workspace" : "Sign in"}</button>
        <button className="link-button" onClick={() => setMode(mode === "register" ? "login" : "register")}>
          {mode === "register" ? "Already have an account? Sign in" : "Need an account? Register"}
        </button>
      </div>
    </div>
  );
}

function CreateProject({
  channels,
  profiles,
  onCreated,
}: {
  channels: Channel[];
  profiles: ContentProfile[];
  onCreated: () => Promise<void>;
}) {
  const [name, setName] = useState("");
  const [channelId, setChannelId] = useState("");
  const [profileId, setProfileId] = useState("");
  const [source, setSource] = useState("");
  const [videoType, setVideoType] = useState<"short" | "long">("long");
  const [duration, setDuration] = useState(300);
  const [quantity, setQuantity] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const durationLabel = useMemo(() => {
    if (duration < 60) return `${duration}s`;
    return `${Math.floor(duration / 60)}m ${duration % 60}s`;
  }, [duration]);

  async function submit() {
    setBusy(true);
    setError("");
    try {
      await api.createProject({
        name,
        channel_id: channelId || undefined,
        content_profile_id: profileId || undefined,
        settings: {
          source_text: source,
          video_type: videoType,
          duration_seconds: duration,
          quantity,
          approval_mode: "manual",
        },
      });
      await onCreated();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to create project");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel form-panel">
      <p className="eyebrow">CONTENT CREATOR</p>
      <h2>Create a project</h2>
      <p className="muted">This creates the structured project that future AI workers will process.</p>

      <label>Project name<input value={name} onChange={(e) => setName(e.target.value)} placeholder="The little fox and the moon" /></label>
      <label>Source / transcript<textarea value={source} onChange={(e) => setSource(e.target.value)} placeholder="Paste an idea, transcript or source text..." /></label>

      <div className="form-grid">
        <label>Channel
          <select value={channelId} onChange={(e) => setChannelId(e.target.value)}>
            <option value="">Select later</option>
            {channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>

        <label>Content profile
          <select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
            <option value="">Select later</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>

        <label>Video type
          <select value={videoType} onChange={(e) => setVideoType(e.target.value as "short" | "long")}>
            <option value="short">Short / Reel</option>
            <option value="long">Long video</option>
          </select>
        </label>

        <label>Duration ({durationLabel})
          <input type="range" min={15} max={600} step={15} value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
        </label>

        <label>Quantity
          <input type="number" min={1} max={100} value={quantity} onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))} />
        </label>
      </div>

      {error && <div className="error">{error}</div>}
      <button className="primary" disabled={!name.trim() || busy} onClick={() => void submit()}>
        {busy ? "Creating..." : "Create project"}
      </button>
    </section>
  );
}
