# Phase 62 — Visual Quality Gate

Adds a deterministic visual artifact quality gate. It checks artifact existence
and duration alignment and returns a retry/manual-review signal.

A future Vision-Language Model (VLM) adapter can add semantic checks without
changing this contract.
