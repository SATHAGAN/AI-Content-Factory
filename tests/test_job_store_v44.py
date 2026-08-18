from pathlib import Path

from app.services.job_store.models import (
    JobRecord,SceneRecord,SceneStatus,PersistentJobStatus
)
from app.services.job_store.sqlite_store import SQLiteJobStore
from app.services.job_store.resume_service import ResumeService
from app.services.job_store.retry_policy import RetryPolicy
from app.services.job_store.recovery import RecoveryManager


def make_store(tmp_path):
    return SQLiteJobStore(str(tmp_path/"jobs.sqlite3"))


def test_job_and_scene_state_persist(tmp_path):
    store=make_store(tmp_path)
    store.create_job(
        job_id="job1",
        channel_id="facts",
        target_duration_seconds=300,
    )
    store.add_scenes([
        SceneRecord("job1","scene-1",1,SceneStatus.PENDING),
        SceneRecord("job1","scene-2",2,SceneStatus.PENDING),
    ])

    store.update_scene(
        "job1","scene-1",
        status=SceneStatus.COMPLETED,
        attempts=1,
        video_path="/v/1.mp4",
        audio_path="/a/1.wav",
    )

    assert store.get_job("job1").status==PersistentJobStatus.CREATED
    scenes=store.list_scenes("job1")
    assert scenes[0].status==SceneStatus.COMPLETED
    assert scenes[0].video_path=="/v/1.mp4"
    assert scenes[1].status==SceneStatus.PENDING


def test_resume_skips_completed_scene(tmp_path):
    store=make_store(tmp_path)
    store.create_job(
        job_id="job2",
        channel_id="kids",
        target_duration_seconds=300,
    )
    store.add_scenes([
        SceneRecord("job2","scene-1",1,SceneStatus.COMPLETED),
        SceneRecord("job2","scene-2",2,SceneStatus.FAILED,attempts=1),
        SceneRecord("job2","scene-3",3,SceneStatus.PENDING),
    ])

    resumable=ResumeService(store).resumable("job2")
    assert [s.scene_id for s in resumable]==["scene-2","scene-3"]


def test_retry_policy(tmp_path):
    policy=RetryPolicy(3)
    assert policy.can_retry(0)
    assert policy.can_retry(2)
    assert not policy.can_retry(3)
    assert policy.next_attempt(2)==3


def test_recovery_marks_running_scene_retryable(tmp_path):
    store=make_store(tmp_path)
    store.create_job(
        job_id="job3",
        channel_id="facts",
        target_duration_seconds=100,
    )
    store.add_scenes([
        SceneRecord("job3","scene-1",1,SceneStatus.RUNNING,attempts=1),
        SceneRecord("job3","scene-2",2,SceneStatus.COMPLETED,attempts=1),
    ])

    recovered=RecoveryManager(store).recover_interrupted_job("job3")
    assert recovered==["scene-1"]
    assert store.list_scenes("job3")[0].status==SceneStatus.FAILED
    assert store.list_scenes("job3")[1].status==SceneStatus.COMPLETED
