from __future__ import annotations

import os

import httpx

from app.services.publishing.interfaces import PublishRequest, PublishResult


class InstagramPublisher:
    """Meta Graph API adapter boundary.

    Instagram publishing requires the appropriate professional account,
    permissions and Meta access token. The exact API version is configurable.
    """

    def __init__(
        self,
        access_token: str | None = None,
        account_id: str | None = None,
        graph_base_url: str | None = None,
    ):
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.account_id = account_id or os.getenv("INSTAGRAM_ACCOUNT_ID", "")
        self.graph_base_url = (
            graph_base_url or os.getenv("META_GRAPH_BASE_URL", "https://graph.facebook.com")
        ).rstrip("/")

    def publish(self, request: PublishRequest) -> PublishResult:
        if not self.access_token or not self.account_id:
            raise RuntimeError("Instagram access token/account id are not configured")

        # This phase establishes the provider contract. The production worker
        # should create a media container, wait for processing, then publish it.
        raise NotImplementedError(
            "Instagram container/publish flow is reserved for the credentialed integration test"
        )
