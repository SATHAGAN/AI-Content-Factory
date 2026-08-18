# Phase 60 — Provider-Neutral Visual Generation

Creates one dynamic contract for scene visuals. A scene may request an image
or video, and the model/provider can be selected without changing orchestration.

The first implementation is a deterministic mock provider. Real model adapters
can be plugged into the same contract later.
