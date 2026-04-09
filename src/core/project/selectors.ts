import type { ContentItem } from "../../domain/content-item.js";
import type { ProjectConfig } from "../../domain/project.js";

export function filterProjects(projects: ProjectConfig[], projectName?: string): ProjectConfig[] {
  if (!projectName || projectName === "all") {
    return projects;
  }

  return projects.filter((project) => project.name === projectName);
}

export function selectContentForProject(
  items: ContentItem[],
  project: ProjectConfig,
  agent: string
): ContentItem[] {
  return items.filter((item) => {
    if (item.targets && !item.targets.includes(agent)) {
      return false;
    }

    if (item.projects && !item.projects.includes(project.name)) {
      return false;
    }

    if (item.status && item.status !== "active") {
      return false;
    }

    const itemTags = item.tags ?? [];
    if (project.includeTags.length > 0 && !itemTags.some((tag) => project.includeTags.includes(tag))) {
      return false;
    }

    if (itemTags.some((tag) => project.excludeTags.includes(tag))) {
      return false;
    }

    return true;
  });
}
