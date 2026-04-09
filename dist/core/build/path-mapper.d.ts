import type { ContentItem } from "../../domain/content-item.js";
import type { AgentConfig, ProjectConfig } from "../../domain/project.js";
export declare function mapOutputPath(item: ContentItem, project: ProjectConfig, agentConfig: AgentConfig): string;
