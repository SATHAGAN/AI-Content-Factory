"""publishing and scheduling foundation

Revision ID: 0002_publishing
Revises: 0001_initial
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_publishing"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade():
    op.create_table(
        "publications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform_account_id", sa.String(36), sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="SET NULL")),
        sa.Column("format", sa.Enum("SHORT", "LONG", name="contentformat"), nullable=False),
        sa.Column("status", sa.Enum(
            "DRAFT", "PENDING_APPROVAL", "APPROVED", "SCHEDULED",
            "UPLOADING", "PUBLISHED", "FAILED", "BLOCKED", "CANCELLED",
            name="publishstatus"
        ), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("external_post_id", sa.String(255)),
        sa.Column("media_uri", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("caption", sa.Text()),
        sa.Column("tags", json_type(), nullable=False),
        sa.Column("metadata", json_type(), nullable=False),
        sa.Column("last_error", sa.Text()),
    )


def downgrade():
    op.drop_table("publications")
    if op.get_context().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS contentformat")
        op.execute("DROP TYPE IF EXISTS publishstatus")
