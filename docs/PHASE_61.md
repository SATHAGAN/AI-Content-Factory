# Phase 61 — Scene Planner → Visual Generation

Connects every planned scene to the selectable visual provider.

```text
StoryPlan → Scene 1..N → VisualRequest → VisualProvider → Asset 1..N
```

No scene is skipped, and scene metadata such as sequence, camera and motion is
passed to the provider.
