import os
import subprocess
import sys


def test_migrations_upgrade_and_downgrade(tmp_path):
    db = tmp_path / "migration.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db.name}"

    up = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=os.getcwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert up.returncode == 0, up.stderr

    down = subprocess.run(
        ["alembic", "downgrade", "base"],
        cwd=os.getcwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert down.returncode == 0, down.stderr
