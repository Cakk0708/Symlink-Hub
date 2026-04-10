# Symlink-Hub

Local AI configuration content hub and distribution CLI.

## Overview

Manage AI coding configurations (agents, skills, rules, docs, commands) in one place and distribute them to multiple projects.

## Tech Stack

- **Go 1.26** - Core CLI implementation
- **YAML** - Configuration format
- **Markdown + Frontmatter** - Content format

## Project Structure

```
Symlink-Hub/
├── cmd/
│   └── symlink-hub/          # CLI entry point
├── internal/
│   ├── core/                 # Core types and interfaces
│   ├── config/               # Configuration models
│   ├── content/              # Content scanning and parsing
│   ├── project/              # Project loading and selectors
│   ├── builder/              # Build plan generation
│   ├── distributor/          # File distribution (symlink/copy)
│   └── agent/                # Agent-specific logic
├── fixtures/
│   ├── content/              # Example content
│   └── projects/             # Example project configs
└── docs/                     # Design documents
```

## Design Documents

- [PRD](docs/v1.0/PRD.md)
- [System Design](docs/v1.0/System-Design.md)

## Quick Start

```bash
# Build
go build -o symlink-hub cmd/symlink-hub/main.go

# Run
./symlink-hub sync backend --agent codex
```

## Commands

- `sync` - Distribute content to projects
- `dry-run` - Preview build plan without changes
- `clean` - Remove distributed files
- `status` - Show sync status
- `doctor` - Check configuration health
