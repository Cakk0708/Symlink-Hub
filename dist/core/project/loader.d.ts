import { type AppConfig } from "../../domain/project.js";
export declare function resolveConfigPath(cwd: string): Promise<string>;
export declare function loadAppConfig(cwd: string): Promise<AppConfig>;
