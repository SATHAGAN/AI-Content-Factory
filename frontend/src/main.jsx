import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import {api} from "./lib/api";
import {Toast} from "./components/Toast";
import "./styles.css";

const channels=[{id:"kids",name:"Kids Stories",platforms:"YouTube · Instagram",shorts:5,long:2},{id:"facts",name:"Daily Facts",platforms:"YouTube · Instagram",shorts:3,long:1}];
const cats=["Kids","Educational","Facts","Motivation","Creative","General"];

function Field({label,children}){return <label className="field"><span>{label}</span>{children}</label>}

function App(){
 const [page,setPage]=useState("create"),[source,setSource]=useState(""),[category,setCategory]=useState("Kids"),[format,setFormat]=useState("short");
 const [duration,setDuration]=useState(60),[language,setLanguage]=useState("English"),[tone,setTone]=useState("Engaging");
 const [video,setVideo]=useState("Wan2.1 T2V 1.3B"),[tts,setTts]=useState("Qwen3-TTS 0.6B"),[judge,setJudge]=useState("Local Multimodal Judge");
 const [approval,setApproval]=useState(true),[auto,setAuto]=useState(false),[selected,setSelected]=useState(["kids"]);
 const [jobs,setJobs]=useState([]),[toast,setToast]=useState(""),[token,setToken]=useState(localStorage.getItem("acf_token")||"");

 async function refreshJobs(){if(!token)return;try{setJobs(await api.listJobs(token))}catch(e){setToast(e.message)}}
 useEffect(()=>{refreshJobs()},[token]);
 useEffect(()=>{if(page!=="queue"||!token)return;const id=setInterval(refreshJobs,1500);return()=>clearInterval(id)},[page,token]);

 function toggle(id){setSelected(x=>x.includes(id)?x.filter(v=>v!==id):[...x,id])}
 async function generate(){
  if(!source.trim()||!selected.length||!token)return;
  try{
   const p=await api.createProject({name:source.trim().slice(0,55),category,language,format,duration_seconds:duration,source_text:source,channel_ids:selected,video_model:video,tts_model:tts,judge_model:judge,approval_required:approval,auto_publish:auto},token);
   await api.enqueueGeneration(p.id,token);await refreshJobs();setPage("queue");setToast("Generation started.");
  }catch(e){setToast(e.message)}
 }

 const stageLabel=s=>({queued:"Queued",planning:"Planning",generating:"Generating scenes",voice:"Generating voice",rendering:"Rendering",media_qa:"Media QA",ai_judge:"AI quality judge",approval:"Awaiting approval",published:"Published",failed:"Failed"}[s]||s);

 return <div className="shell"><aside><div className="brand">✦ <b>Content Factory</b></div>
 {["create","queue","channels","models","settings"].map(p=><button className={page===p?"nav active":"nav"} onClick={()=>setPage(p)} key={p}>{p==="create"?"Create":p==="queue"?"Generation Queue":p[0].toUpperCase()+p.slice(1)}</button>)}
 <div className="ready">● Worker online</div></aside>
 <main><header><div><small>AI CONTENT FACTORY</small><h1>{page==="create"?"Create content":page==="queue"?"Generation queue":page[0].toUpperCase()+page.slice(1)}</h1></div><span className="pill">Pipeline worker active</span></header>
 {page==="create"&&<div className="layout"><section className="card">
 <h3>1. Content source</h3><p>Paste a transcript, idea, script, or source text.</p>
 <textarea value={source} onChange={e=>setSource(e.target.value)} placeholder="Example: A young fox gets lost in a forest and learns why asking for help is a strength..."/>
 <div className="two"><Field label="Category"><select value={category} onChange={e=>setCategory(e.target.value)}>{cats.map(x=><option key={x}>{x}</option>)}</select></Field><Field label="Language"><select value={language} onChange={e=>setLanguage(e.target.value)}>{["English","Tamil","Hindi","Telugu","Malayalam"].map(x=><option key={x}>{x}</option>)}</select></Field></div>
 <h3 className="gap">2. Video configuration</h3><div className="seg"><button className={format==="short"?"sel":""} onClick={()=>{setFormat("short");setDuration(60)}}>Short</button><button className={format==="long"?"sel":""} onClick={()=>{setFormat("long");setDuration(300)}}>Long video</button></div>
 <Field label={`Target duration · ${Math.floor(duration/60)}m ${duration%60}s`}><input type="range" min="15" max="600" step="15" value={duration} onChange={e=>setDuration(+e.target.value)}/></Field>
 <div className="two"><Field label="Tone"><select value={tone} onChange={e=>setTone(e.target.value)}>{["Engaging","Funny","Educational","Emotional","Calm"].map(x=><option key={x}>{x}</option>)}</select></Field><Field label="Video model"><select value={video} onChange={e=>setVideo(e.target.value)}><option>Wan2.1 T2V 1.3B</option><option>Wan2.2</option><option>LTX Video</option></select></Field></div>
 <div className="two"><Field label="Voice model"><select value={tts} onChange={e=>setTts(e.target.value)}><option>Qwen3-TTS 0.6B</option><option>Qwen3-TTS 1.7B</option></select></Field><Field label="Quality judge"><select value={judge} onChange={e=>setJudge(e.target.value)}><option>Local Multimodal Judge</option><option>Cloud Multimodal Judge</option></select></Field></div>
 </section><div className="stack"><section className="card"><h3>3. Publish targets</h3><p>One generation can target multiple channels.</p>{channels.map(c=><label className="channel" key={c.id}><input type="checkbox" checked={selected.includes(c.id)} onChange={()=>toggle(c.id)}/><span><b>{c.name}</b><small>{c.platforms}</small></span><em>{c.shorts}S · {c.long}L/day</em></label>)}<hr/><label className="switch"><span><b>Manual approval</b><small>Review before publishing</small></span><input type="checkbox" checked={approval} onChange={e=>setApproval(e.target.checked)}/></label><label className="switch"><span><b>Auto publish</b><small>Enable after validation</small></span><input type="checkbox" checked={auto} onChange={e=>setAuto(e.target.checked)}/></label></section>
 <section className="card"><h3>Generation plan</h3><div className="row"><span>Format</span><b>{format}</b></div><div className="row"><span>Duration</span><b>{duration}s</b></div><div className="row"><span>Channels</span><b>{selected.length}</b></div><button className="primary" disabled={!source.trim()||!selected.length||!token} onClick={generate}>{token?"Generate content →":"Connect API first"}</button></section></div></div>}
 {page==="queue"&&<section className="card page"><div className="head"><div><h3>Live generation queue</h3><p>Worker progress refreshes automatically.</p></div><button onClick={refreshJobs}>↻ Refresh</button></div>{!jobs.length?<div className="empty">No jobs yet.</div>:jobs.map(j=><div className="job" key={j.id}><b>AI</b><span><strong>{j.id.slice(0,12)}</strong><small>{stageLabel(j.stage)} · {j.message}</small><div className="bar"><i style={{width:`${j.progress}%`}}/></div></span><em>{j.progress}%</em></div>)}</section>}
 {page==="channels"&&<section className="card page"><h3>Connected channels</h3>{channels.map(c=><div className="channel-card" key={c.id}><b>{c.name[0]}</b><span><strong>{c.name}</strong><small>{c.platforms}</small></span><em>Configured</em></div>)}</section>}
 {page==="models"&&<section className="models">{["Wan2.1 T2V 1.3B · Video","Qwen3-TTS 0.6B · Voice","Local Multimodal Judge · QA","Mock providers · Development"].map(x=><div className="card model" key={x}><b>AI</b><span>{x}</span><em>Configurable</em></div>)}</section>}
 {page==="settings"&&<section className="card page"><h3>System settings</h3><div className="setting"><b>Worker</b><span>Background task pipeline</span></div><div className="setting"><b>Storage</b><span>Google Cloud Storage adapter</span></div><div className="setting"><b>Approval</b><span>Manual by default</span></div></section>}
 </main><Toast message={toast}/></div>
}
createRoot(document.getElementById("root")).render(<App/>);
