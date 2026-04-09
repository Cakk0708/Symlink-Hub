import type { BuildPlan } from "../../domain/build-plan.js";
import type { ProjectConfig } from "../../domain/project.js";
export interface DryRunOptions {
    cwd: string;
    projectName?: string;
    agent?: string;
}
export interface DryRunResult {
    plans: BuildPlan[];
    projects: ProjectConfig[];
}
export declare function runDryRun(options: DryRunOptions): Promise<DryRunResult>;
