# Local Modifications

This document describes the Douglax local changes on top of upstream Pianke.

## Summary

The local fork adds practical workflow improvements for larger photo-selection jobs:

- More robust resume behavior for long-running or large-folder selection work.
- Front-end UI improvements for managing larger projects.
- macOS launcher scripts for a local workflow mounted from an external SSD.

## User-Facing Changes To Document Before Release

- Which project states can resume after restart.
- Where session/progress files are stored.
- What happens when a photo folder is moved, renamed, or partially processed.
- Whether resume behavior is compatible with upstream project sessions.
- Which UI screens differ from upstream.
- Which keyboard or review workflows were added or changed.

## Files Likely To Review Before Publishing

- `app.py`
- `static/app.js`
- `static/index.html`
- `static/style.css`
- `tests/test_prescreen_session.py`
- `启动-片刻专家版.command`
- `后台启动-片刻专家版.command`
- `停止-片刻专家版.command`
- `圆心-选片接入说明.md`

## Non-Publishable Local Runtime Data

Do not publish local runtime data:

- `.venv/`
- `models/`
- `workspace/`
- `*.log`
- `*.pid`
- `.pytest_cache/`
- `__pycache__/`
- local photo folders
- model caches

These are already mostly covered by `.gitignore`, but should be checked before pushing a public repository.
