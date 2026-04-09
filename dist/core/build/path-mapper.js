import path from "node:path";
export function mapOutputPath(item, project, agentConfig) {
    if (item.type === "agent") {
        return path.join(project.path, agentConfig.agentFileName);
    }
    const rootDir = agentConfig.roots[item.type];
    return path.join(project.path, rootDir, `${item.id}.md`);
}
//# sourceMappingURL=path-mapper.js.map