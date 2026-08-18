from app.services.deployment.config import DeploymentConfig,validate_production
from app.services.deployment.health import ComponentHealth


def test_production_validation_requires_durable_storage_and_scheduler():
    errors=validate_production(DeploymentConfig(
        environment="production",
        storage_provider="local",
        scheduler_enabled=False,
    ))
    assert len(errors)==2


def test_health_snapshot():
    health=ComponentHealth()
    health.set("database","ok")
    health.set("storage","ok")
    assert health.snapshot()["status"]=="ok"
    health.set("llm","degraded","worker unavailable")
    assert health.snapshot()["status"]=="degraded"
