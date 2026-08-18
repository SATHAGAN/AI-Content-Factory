"""initial foundation

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-16
"""
from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("default_language", sa.String(32), nullable=False),
        sa.Column("approval_mode", sa.Enum("MANUAL", "HYBRID", "AUTOMATIC", name="approvalmode"), nullable=False),
        sa.Column("daily_shorts_target", sa.Integer(), nullable=False),
        sa.Column("daily_long_target", sa.Integer(), nullable=False),
        sa.Column("settings", json_type(), nullable=False),
    )
    op.create_table(
        "platform_accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.Enum("YOUTUBE", "INSTAGRAM", name="platform"), nullable=False),
        sa.Column("external_account_id", sa.String(255)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("credentials_ref", sa.String(512)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("metadata", json_type(), nullable=False),
        sa.UniqueConstraint("channel_id", "platform", name="uq_channel_platform"),
    )
    op.create_table(
        "content_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("audience", sa.String(160)),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("tone", sa.String(100)),
        sa.Column("settings", json_type(), nullable=False),
        sa.UniqueConstraint("organization_id", "name", name="uq_profile_org_name"),
    )
    op.create_table(
        "source_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.Enum("PROMPT", "TRANSCRIPT", "TEXT", "PDF", "DOCX", "URL", "AUDIO", "VIDEO", name="sourcetype"), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("content_text", sa.Text()),
        sa.Column("storage_uri", sa.String(1024)),
        sa.Column("metadata", json_type(), nullable=False),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", sa.String(36), sa.ForeignKey("channels.id", ondelete="SET NULL")),
        sa.Column("content_profile_id", sa.String(36), sa.ForeignKey("content_profiles.id", ondelete="SET NULL")),
        sa.Column("source_document_id", sa.String(36), sa.ForeignKey("source_documents.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("settings", json_type(), nullable=False),
    )
    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("job_type", sa.String(80), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "RETRYING", name="jobstatus"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(100)),
        sa.Column("error_message", sa.Text()),
        sa.Column("input_data", json_type(), nullable=False),
        sa.Column("output_data", json_type(), nullable=False),
    )
    op.create_table(
        "model_registry",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("model_id", sa.String(255), nullable=False),
        sa.Column("capability", sa.Enum("LLM", "VIDEO", "IMAGE", "TTS", "MUSIC", "MODERATION", name="modelcapability"), nullable=False),
        sa.Column("version", sa.String(100)),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("config", json_type(), nullable=False),
        sa.UniqueConstraint("provider", "model_id", name="uq_provider_model"),
    )


def downgrade():
    op.drop_table("model_registry")
    op.drop_table("generation_jobs")
    op.drop_table("projects")
    op.drop_table("source_documents")
    op.drop_table("content_profiles")
    op.drop_table("platform_accounts")
    op.drop_table("channels")
    op.drop_table("users")
    op.drop_table("organizations")
    if context.get_context().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS modelcapability")
        op.execute("DROP TYPE IF EXISTS jobstatus")
        op.execute("DROP TYPE IF EXISTS sourcetype")
        op.execute("DROP TYPE IF EXISTS platform")
        op.execute("DROP TYPE IF EXISTS approvalmode")
