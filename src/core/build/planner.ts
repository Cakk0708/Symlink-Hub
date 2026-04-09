import fs from "fs-extra";
import type { BuildPlan, BuildPlanEntry, DistributionMode } from "../../domain/build-plan.js";
import type { ContentItem } from "../../domain/content-item.js";
import type { AgentConfig, ProjectConfig } from "../../domain/project.js";
import { mapOutputPath } from "./path-mapper.js";

function createEntry(
  item: ContentItem,
  project: ProjectConfig,
  agent: string,
  agentConfig: AgentConfig,
  mode: DistributionMode,
  action: BuildPlanEntry["action"],
  reason?: string
): BuildPlanEntry {
  const entry: BuildPlanEntry = {
    action,
    projectName: project.name,
    agent,
    sourceItemIds: [item.id],
    outputPath: mapOutputPath(item, project, agentConfig),
    mode
  };

  if (reason) {
    entry.reason = reason;
  }

  return entry;
}

export async function buildPlanForProject(
  items: ContentItem[],
  project: ProjectConfig,
  agent: string,
  agentConfig: AgentConfig,
  mode: DistributionMode
): Promise<BuildPlan> {
  const entries: BuildPlanEntry[] = [];
  const agentItems = items.filter((item) => item.type === "agent");

  if (agentItems.length > 1) {
    const firstAgentItem = agentItems[0];
    if (!firstAgentItem) {
      throw new Error("Expected at least one agent content item.");
    }

    const conflictPath = mapOutputPath(firstAgentItem, project, agentConfig);
    entries.push({
      action: "conflict",
      projectName: project.name,
      agent,
      sourceItemIds: agentItems.map((item) => item.id),
      outputPath: conflictPath,
      mode,
      reason: "Multiple agent content items matched the same output."
    });
  }

  for (const item of items) {
    if (item.type === "agent" && agentItems.length > 1) {
      continue;
    }

    const outputPath = mapOutputPath(item, project, agentConfig);
    const exists = await fs.pathExists(outputPath);

    entries.push(
      createEntry(
        item,
        project,
        agent,
        agentConfig,
        mode,
        exists ? "replace" : "create"
      )
    );
  }

  return {
    generatedAt: new Date().toISOString(),
    entries
  };
}
