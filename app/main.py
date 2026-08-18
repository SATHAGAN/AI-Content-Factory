from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    artifacts, auth, channels, content, content_profiles, generation,
    health, jobs, judge, projects, qa, render, sources, publishing,
    scheduling, workspace, content_planning,
)

app=FastAPI(title="AI Content Factory API",version="1.5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
for router in [
    auth.router,channels.router,content_profiles.router,sources.router,
    projects.router,content.router,jobs.router,generation.router,
    artifacts.router,render.router,qa.router,judge.router,publishing.router,
    scheduling.router,workspace.router,content_planning.router
]:
    app.include_router(router,prefix="/api/v1")
