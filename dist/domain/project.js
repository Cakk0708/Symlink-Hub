import { z } from "zod";
import { SUPPORTED_CONFLICT_POLICIES, SUPPORTED_DISTRIBUTION_MODES, SUPPORTED_CONTENT_TYPES } from "../config/constants.js";
const modeSchema = z.enum(SUPPORTED_DISTRIBUTION_MODES);
const conflictSchema = z.enum(SUPPORTED_CONFLICT_POLICIES);
const agentRootsSchema = z.object({
    skill: z.string().min(1),
    rule: z.string().min(1),
    doc: z.string().min(1),
    command: z.string().min(1)
});
export const agentConfigSchema = z.object({
    agentFileName: z.string().min(1),
    roots: agentRootsSchema
});
export const projectConfigSchema = z.object({
    name: z.string().min(1),
    path: z.string().min(1),
    agents: z.array(z.string().min(1)).min(1),
    includeTags: z.array(z.string().min(1)).default([]),
    excludeTags: z.array(z.string().min(1)).default([]),
    features: z.array(z.string().min(1)).default([]),
    mode: modeSchema.optional(),
    conflict: conflictSchema.optional()
});
export const appConfigSchema = z.object({
    contentRoot: z.string().min(1),
    stateRoot: z.string().min(1),
    defaultMode: modeSchema,
    agents: z.record(z.string(), agentConfigSchema),
    projects: z.array(projectConfigSchema).min(1)
});
export const supportedMappedTypes = SUPPORTED_CONTENT_TYPES.filter((type) => type !== "agent");
//# sourceMappingURL=project.js.map