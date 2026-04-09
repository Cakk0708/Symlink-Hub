import { formatBuildPlan } from "../../core/build/format.js";
import { runDryRun } from "../../core/app/dry-run.js";
import { info } from "../../utils/logger.js";

export interface DryRunCommandOptions {
  agent?: string;
}

export async function runDryRunCommand(
  projectName: string | undefined,
  options: DryRunCommandOptions
): Promise<void> {
  const cwd = process.cwd();
  const result = await runDryRun(
    {
      cwd,
      ...(projectName ? { projectName } : {}),
      ...(options.agent ? { agent: options.agent } : {})
    }
  );

  for (const plan of result.plans) {
    info(`Build plan generated at ${plan.generatedAt}`);
    console.log(formatBuildPlan(plan));
    console.log("");
  }
}
