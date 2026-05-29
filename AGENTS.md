# CareerChat — Agent Guide

## Project state

Empty skeleton repo. No source code, no package manager, no build/test/lint tooling, no CI. Single commit on `main`.

## Environment

- **Dev container**: `mcr.microsoft.com/devcontainers/universal:4.0.1-noble` (image only, no Dockerfile).
- **Container name** in devcontainer.json is `"Ona"`.
- **Recommended extension**: `sst-dev.opencode` (VS Code).
- **Git LFS** is enabled.

## Git

- `.ona/review` and `.ona/artifacts` are in `.git/info/exclude` (never tracked).
- Remote: `origin` → `https://github.com/limynet/CareerChat.git`.
