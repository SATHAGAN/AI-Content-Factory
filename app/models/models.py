from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.enums import ApprovalMode, ContentFormat, JobStatus, ModelCapability, Platform, PublishStatus, SourceType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


JsonType = JSON().with_variant(JSONB, "postgresql")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    channels: Mapped[list["Channel"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_user_org_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(320))
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization: Mapped["Organization"] = relationship(back_populates="users")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    default_language: Mapped[str] = mapped_column(String(32), default="en")
    approval_mode: Mapped[ApprovalMode] = mapped_column(Enum(ApprovalMode), default=ApprovalMode.MANUAL)
    daily_shorts_target: Mapped[int] = mapped_column(Integer, default=0)
    daily_long_target: Mapped[int] = mapped_column(Integer, default=0)
    settings: Mapped[dict] = mapped_column(JsonType, default=dict)

    organization: Mapped["Organization"] = relationship(back_populates="channels")
    platform_accounts: Mapped[list["PlatformAccount"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"
    __table_args__ = (
        UniqueConstraint("channel_id", "platform", name="uq_channel_platform"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"))
    platform: Mapped[Platform] = mapped_column(Enum(Platform))
    external_account_id: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    credentials_ref: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)

    channel: Mapped["Channel"] = relationship(back_populates="platform_accounts")


class ContentProfile(Base):
    __tablename__ = "content_profiles"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_profile_org_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(100))
    audience: Mapped[str | None] = mapped_column(String(160))
    language: Mapped[str] = mapped_column(String(32), default="en")
    tone: Mapped[str | None] = mapped_column(String(100))
    settings: Mapped[dict] = mapped_column(JsonType, default=dict)


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    title: Mapped[str | None] = mapped_column(String(255))
    content_text: Mapped[str | None] = mapped_column(Text)
    storage_uri: Mapped[str | None] = mapped_column(String(1024))
    extra_metadata: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    channel_id: Mapped[str | None] = mapped_column(ForeignKey("channels.id", ondelete="SET NULL"))
    content_profile_id: Mapped[str | None] = mapped_column(ForeignKey("content_profiles.id", ondelete="SET NULL"))
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("source_documents.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    settings: Mapped[dict] = mapped_column(JsonType, default=dict)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    job_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    schedule_key: Mapped[str | None] = mapped_column(String(255), unique=True)
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    input_data: Mapped[dict] = mapped_column(JsonType, default=dict)
    output_data: Mapped[dict] = mapped_column(JsonType, default=dict)


class ModelRegistry(Base):
    __tablename__ = "model_registry"
    __table_args__ = (UniqueConstraint("provider", "model_id", name="uq_provider_model"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(100))
    model_id: Mapped[str] = mapped_column(String(255))
    capability: Mapped[ModelCapability] = mapped_column(Enum(ModelCapability))
    version: Mapped[str | None] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[dict] = mapped_column(JsonType, default=dict)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"))
    platform_account_id: Mapped[str] = mapped_column(ForeignKey("platform_accounts.id", ondelete="CASCADE"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    format: Mapped[ContentFormat] = mapped_column(Enum(ContentFormat))
    status: Mapped[PublishStatus] = mapped_column(Enum(PublishStatus), default=PublishStatus.DRAFT)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_post_id: Mapped[str | None] = mapped_column(String(255))
    media_uri: Mapped[str] = mapped_column(String(2048))
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JsonType, default=list)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    last_error: Mapped[str | None] = mapped_column(Text)
