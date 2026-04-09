export type BuildAction = "create" | "replace" | "skip" | "conflict";
export type DistributionMode = "symlink" | "copy";
export interface BuildPlanEntry {
    action: BuildAction;
    projectName: string;
    agent: string;
    sourceItemIds: string[];
    outputPath: string;
    mode: DistributionMode;
    reason?: string;
}
export interface BuildPlan {
    generatedAt: string;
    entries: BuildPlanEntry[];
}
