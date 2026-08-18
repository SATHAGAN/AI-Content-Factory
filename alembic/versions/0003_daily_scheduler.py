"""add persistent daily scheduling keys

Revision ID: 0003_daily_scheduler
Revises: 0002_publishing
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_daily_scheduler"
down_revision = "0002_publishing"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("generation_jobs", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("schedule_key", sa.String(255), nullable=True))
        batch_op.create_unique_constraint("uq_generation_job_schedule_key", ["schedule_key"])


def downgrade():
    with op.batch_alter_table("generation_jobs", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_generation_job_schedule_key", type_="unique")
        batch_op.drop_column("schedule_key")
