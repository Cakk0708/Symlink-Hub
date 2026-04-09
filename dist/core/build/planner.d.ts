import type { BuildPlan, DistributionMode } from "../../domain/build-plan.js";
import type { ContentItem } from "../../domain/content-item.js";
import type { AgentConfig, ProjectConfig } from "../../domain/project.js";
export declare function buildPlanForProject(items: ContentItem[], project: ProjectConfig, agent: string, agentConfig: AgentConfig, mode: DistributionMode): Promise<BuildPlan>;
