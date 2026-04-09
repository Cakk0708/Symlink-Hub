import path from "node:path";
import type { ContentItem } from "../../domain/content-item.js";
import type { AgentConfig, ProjectConfig } from "../../domain/project.js";

export function mapOutputPath(
  item: ContentItem,
  project: ProjectConfig,
  agentConfig: AgentConfig
): string {
  if (item.type === "agent") {
    return path.join(project.path, agentConfig.agentFileName);
  }

  const rootDir = agentConfig.roots[item.type];
  return path.join(project.path, rootDir, `${item.id}.md`);
}
