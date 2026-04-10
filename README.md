# Symlink-Hub

> Local AI configuration content hub and distribution CLI.

[English](README.md) | [简体中文](README.zh-CN.md)

## Overview

Symlink-Hub is a local tool that manages AI coding configurations (agents, skills, rules, docs, commands) in one place and distributes them to multiple projects based on rules.

## Tech Stack

- **Go 1.26+** - Core CLI implementation
- **YAML** - Configuration format
- **Markdown + Frontmatter** - Content format

## Features

- **Centralized Management**: Manage all AI configuration content in one repository
- **Multi-Agent Support**: Codex, Claude, and extensible to other AI tools
- **Flexible Distribution**: Symlink and copy modes
- **Tag-Based Filtering**: Organize and distribute content by tags
- **Dry-Run Mode**: Preview changes before applying
- **Manifest Tracking**: Track sync history and enable clean rollback

## Project Structure

```
Symlink-Hub/
├── cmd/symlink-hub/     # CLI entry point
├── internal/
│   ├── core/           # Core types
│   ├── config/         # Configuration loading
│   ├── content/        # Content scanning & parsing
│   ├── selector/       # Content selection logic
│   ├── mapper/         # Path mapping
│   ├── planner/        # Build plan generation
│   ├── manifest/       # Sync record management
│   └── distributor/    # File operations
├── fixtures/
│   ├── content/        # Example content
│   └── projects/       # Example projects
└── .claude/docs/       # Module documentation
```

## Quick Start

```bash
# Build
go build -o symlink-hub cmd/symlink-hub/main.go

# Check configuration
./symlink-hub doctor

# Preview changes
./symlink-hub dry-run

# Sync content
./symlink-hub sync

# Clean distributed files
./symlink-hub clean
```

## Commands

| Command | Description |
|---------|-------------|
| `doctor` | Check configuration health |
| `dry-run` | Preview build plan without changes |
| `sync` | Distribute content to projects |
| `clean` | Remove distributed files |
| `status` | Show sync status (coming soon) |

## Configuration

Create `symlink-hub.config.yaml`:

```yaml
contentRoot: ./content
stateRoot: ./.symlink-hub
defaultMode: symlink

agents:
  codex:
    agentFileName: CODEX.md
    roots:
      skill: .codex/skills
      rule: .codex/rules
      doc: .codex/docs
      command: .codex/commands

projects:
  - name: backend
    path: ./projects/backend
    agents: [codex]
    includeTags: [global, backend]
    excludeTags: [experimental]
```

## Content Format

Content files use Markdown with frontmatter:

```markdown
---
id: auth-login
title: Auth Login Skill
type: skill
targets:
  - codex
tags:
  - backend
  - auth
projects:
  - backend
status: active
---

# Auth Login

Implementation guidance for auth login flows.
```

## Documentation

- [PRD](docs/v1.0/PRD.md)
- [System Design](docs/v1.0/System-Design.md)
- [Module Documentation](.claude/docs/map.md)

## License

MIT
