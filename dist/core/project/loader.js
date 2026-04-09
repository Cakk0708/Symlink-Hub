import fs from "fs-extra";
import path from "node:path";
import YAML from "yaml";
import { CONFIG_FILE_NAMES } from "../../config/constants.js";
import { appConfigSchema } from "../../domain/project.js";
import { toAbsolutePath } from "../../utils/paths.js";
export async function resolveConfigPath(cwd) {
    for (const fileName of CONFIG_FILE_NAMES) {
        const candidate = path.join(cwd, fileName);
        if (await fs.pathExists(candidate)) {
            return candidate;
        }
    }
    throw new Error(`No config file found. Expected one of: ${CONFIG_FILE_NAMES.join(", ")}.`);
}
export async function loadAppConfig(cwd) {
    const configPath = await resolveConfigPath(cwd);
    const raw = await fs.readFile(configPath, "utf8");
    const parsed = YAML.parse(raw);
    const configDir = path.dirname(configPath);
    const config = appConfigSchema.parse(parsed);
    return {
        ...config,
        contentRoot: toAbsolutePath(configDir, config.contentRoot),
        stateRoot: toAbsolutePath(configDir, config.stateRoot),
        projects: config.projects.map((project) => ({
            ...project,
            path: toAbsolutePath(configDir, project.path)
        }))
    };
}
//# sourceMappingURL=loader.js.map