import type { BuildPlan } from "../../domain/build-plan.js";
import type { ProjectConfig } from "../../domain/project.js";
import { buildPlanForProject } from "../build/planner.js";
import { scanContent } from "../content/scanner.js";
import { validateUniqueContentIds } from "../content/validators.js";
import { loadAppConfig } from "../project/loader.js";
import { filterProjects, selectContentForProject } from "../project/selectors.js";

export interface DryRunOptions {
  cwd: string;
  projectName?: string;
  agent?: string;
}

export interface DryRunResult {
  plans: BuildPlan[];
  projects: ProjectConfig[];
}

export async function runDryRun(options: DryRunOptions): Promise<DryRunResult> {
  const config = await loadAppConfig(options.cwd);
  const allItems = await scanContent(config.contentRoot);
  validateUniqueContentIds(allItems);

  const projects = filterProjects(config.projects, options.projectName);
  if (projects.length === 0) {
    throw new Error(`No projects matched "${options.projectName}".`);
  }

  const plans: BuildPlan[] = [];

  for (const project of projects) {
    const agents = options.agent ? [options.agent] : project.agents;

    for (const agent of agents) {
      const agentConfig = config.agents[agent];
      if (!agentConfig) {
        throw new Error(`Agent "${agent}" is not defined in config.`);
      }

      if (!project.agents.includes(agent)) {
        throw new Error(`Project "${project.name}" does not enable agent "${agent}".`);
      }

      const selectedItems = selectContentForProject(allItems, project, agent);
      const mode = project.mode ?? config.defaultMode;
      const plan = await buildPlanForProject(selectedItems, project, agent, agentConfig, mode);
      plans.push(plan);
    }
  }

  return { plans, projects };
}
