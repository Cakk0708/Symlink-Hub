#!/usr/bin/env node
import { Command } from "commander";
import { runCleanCommand } from "./commands/clean.js";
import { runDoctorCommand } from "./commands/doctor.js";
import { runDryRunCommand } from "./commands/dry-run.js";
import { runStatusCommand } from "./commands/status.js";
import { runSyncCommand } from "./commands/sync.js";
import { error } from "../utils/logger.js";
const program = new Command();
program
    .name("symlink-hub")
    .description("Local AI configuration content hub.")
    .version("0.1.0");
program
    .command("dry-run")
    .argument("[project]", "Project name or all")
    .option("--agent <agent>", "Run for a specific agent")
    .action(async (project, options) => {
    await runDryRunCommand(project, options);
});
program.command("sync").action(async () => {
    await runSyncCommand();
});
program.command("clean").action(async () => {
    await runCleanCommand();
});
program.command("status").action(async () => {
    await runStatusCommand();
});
program.command("doctor").action(async () => {
    await runDoctorCommand();
});
try {
    await program.parseAsync(process.argv);
}
catch (caught) {
    const message = caught instanceof Error ? caught.message : String(caught);
    error(message);
    process.exitCode = 1;
}
//# sourceMappingURL=index.js.map