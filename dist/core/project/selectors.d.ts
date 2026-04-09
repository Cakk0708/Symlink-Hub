import type { ContentItem } from "../../domain/content-item.js";
import type { ProjectConfig } from "../../domain/project.js";
export declare function filterProjects(projects: ProjectConfig[], projectName?: string): ProjectConfig[];
export declare function selectContentForProject(items: ContentItem[], project: ProjectConfig, agent: string): ContentItem[];
