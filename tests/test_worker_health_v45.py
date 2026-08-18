from datetime import datetime,timezone,timedelta

from app.services.worker.health import WorkerHeartbeat


def test_heartbeat_and_stale_check():
    hb=WorkerHeartbeat()
    hb.beat("gpu-1")
    assert hb.last_seen("gpu-1") is not None
    now=datetime.now(timezone.utc)
    assert not hb.stale("gpu-1",max_age_seconds=60,now=now)


def test_unknown_worker_is_stale():
    hb=WorkerHeartbeat()
    assert hb.stale("missing",max_age_seconds=60)


def test_old_heartbeat_is_stale():
    hb=WorkerHeartbeat()
    hb._last_seen["gpu-1"]=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
    assert hb.stale("gpu-1",max_age_seconds=60)
