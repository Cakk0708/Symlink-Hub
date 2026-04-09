import type { BuildPlan } from "../../domain/build-plan.js";

export function formatBuildPlan(plan: BuildPlan): string {
  if (plan.entries.length === 0) {
    return "No build actions generated.";
  }

  const lines = plan.entries.map((entry) => {
    const reasonSuffix = entry.reason ? ` (${entry.reason})` : "";
    return `${entry.action.toUpperCase()} ${entry.outputPath} <- ${entry.sourceItemIds.join(", ")}${reasonSuffix}`;
  });

  return lines.join("\n");
}
