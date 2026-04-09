export const CONFIG_FILE_NAMES = [
  "symlink-hub.config.yaml",
  "symlink-hub.config.yml"
] as const;

export const SUPPORTED_CONTENT_TYPES = [
  "agent",
  "skill",
  "rule",
  "doc",
  "command"
] as const;

export const SUPPORTED_DISTRIBUTION_MODES = ["symlink", "copy"] as const;

export const SUPPORTED_CONFLICT_POLICIES = [
  "skip",
  "replace",
  "backup"
] as const;
