import fs from "fs-extra";
import { mapOutputPath } from "./path-mapper.js";
function createEntry(item, project, agent, agentConfig, mode, action, reason) {
    const entry = {
        action,
        projectName: project.name,
        agent,
        sourceItemIds: [item.id],
        outputPath: mapOutputPath(item, project, agentConfig),
        mode
    };
    if (reason) {
        entry.reason = reason;
    }
    return entry;
}
export async function buildPlanForProject(items, project, agent, agentConfig, mode) {
    const entries = [];
    const agentItems = items.filter((item) => item.type === "agent");
    if (agentItems.length > 1) {
        const firstAgentItem = agentItems[0];
        if (!firstAgentItem) {
            throw new Error("Expected at least one agent content item.");
        }
        const conflictPath = mapOutputPath(firstAgentItem, project, agentConfig);
        entries.push({
            action: "conflict",
            projectName: project.name,
            agent,
            sourceItemIds: agentItems.map((item) => item.id),
            outputPath: conflictPath,
            mode,
            reason: "Multiple agent content items matched the same output."
        });
    }
    for (const item of items) {
        if (item.type === "agent" && agentItems.length > 1) {
            continue;
        }
        const outputPath = mapOutputPath(item, project, agentConfig);
        const exists = await fs.pathExists(outputPath);
        entries.push(createEntry(item, project, agent, agentConfig, mode, exists ? "replace" : "create"));
    }
    return {
        generatedAt: new Date().toISOString(),
        entries
    };
}
//# sourceMappingURL=planner.js.map