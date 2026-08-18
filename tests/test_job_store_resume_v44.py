from app.services.job_store.models import SceneRecord,SceneStatus
from app.services.job_store.sqlite_store import SQLiteJobStore
from app.services.job_store.resume_service import ResumeService


def test_mark_scene_lifecycle(tmp_path):
    store=SQLiteJobStore(str(tmp_path/"jobs.sqlite3"))
    store.create_job(
        job_id="job4",
        channel_id="facts",
        target_duration_seconds=60,
    )
    store.add_scenes([
        SceneRecord("job4","scene-1",1,SceneStatus.PENDING),
    ])

    resume=ResumeService(store)
    scene=store.list_scenes("job4")[0]
    resume.mark_scene_running(scene)

    running=store.list_scenes("job4")[0]
    assert running.status==SceneStatus.RUNNING
    assert running.attempts==1

    resume.mark_scene_failed(running,"temporary error")
    failed=store.list_scenes("job4")[0]
    assert failed.status==SceneStatus.FAILED

    resume.mark_scene_completed(
        failed,
        video_path="/video.mp4",
        audio_path="/audio.wav",
    )
    completed=store.list_scenes("job4")[0]
    assert completed.status==SceneStatus.COMPLETED
    assert completed.video_path=="/video.mp4"
