# Repository Guidelines

## Project Structure & Module Organization

This repository is a data-driven symlink generator for project workspaces.

- `update_link.py`: main entrypoint; reads config, builds `.links/{project}`, and syncs links into real project paths.
- `data/`: source content and metadata.
  - `config.json`: maps resource IDs to names, tags, structure, and references.
  - `project.json`: project tags and target filesystem paths.
  - `tags.json`: allowed tag catalog.
  - `skills/`, `rules/`, `docs/`, `agents/`, `commands/`, `memory/`, `mcp/`, `others/`, `references/`: source files grouped by resource type.
- `.links/`: generated templates per project. Treat as build output, not hand-edited source.
- `docs/v1.0/`: historical design notes.

## Build, Test, and Development Commands

- `python3 update_link.py`: launch the generator and choose `claude` or `codex`.
- `python3 update_link.py --scheme codex --project duolingo`: generate one project non-interactively.
- `python3 -m py_compile update_link.py`: quick syntax validation before commit.
- `python3 update_link.py --scheme claude`: rebuild all configured projects and overwrite stale links.

Run commands from the repository root.

## Coding Style & Naming Conventions

- Use Python 3 with 4-space indentation and standard library first.
- Keep functions small and explicit; prefer `Path` over string path handling.
- Preserve the current data model: resource IDs map to files in `data/<type>/`.
- Use descriptive snake_case for functions and variables.
- Keep generated filenames aligned with config names, for example `Terms.md`, `launch.json`, `SKILL.md`.

## Testing Guidelines

There is no formal test suite yet. Validate changes with:

- `python3 -m py_compile update_link.py`
- a targeted dry run such as `python3 update_link.py --scheme codex --project duolingo`
- manual inspection of `.links/<project>` and the synced target path

When changing mode-switch behavior, verify both directions: `codex -> claude -> codex`.

## Commit & Pull Request Guidelines

Recent history uses short prefixes such as `Fix:`, `docs:`, `refactor:`, and `feat:`. Prefer:

- `feat: add codex cleanup on mode switch`
- `fix: handle missing reference extension`

PRs should include:

- a concise summary of behavior changes
- affected config or data directories
- validation steps run
- screenshots only if a file-browser or symlink inspection issue is relevant

## Configuration Notes

- Switching modes must remove stale counterparts: `.claude`/`CLAUDE.md` vs `.codex`/`AGENTS.md`.
- `data/tags.json` is authoritative; new tags should be added there before use.
