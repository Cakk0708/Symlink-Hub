import { z } from "zod";
import { SUPPORTED_CONTENT_TYPES } from "../config/constants.js";
export const contentTypeSchema = z.enum(SUPPORTED_CONTENT_TYPES);
export const contentFrontmatterSchema = z.object({
    id: z.string().min(1),
    title: z.string().min(1),
    type: contentTypeSchema,
    targets: z.array(z.string().min(1)).optional(),
    tags: z.array(z.string().min(1)).optional(),
    projects: z.array(z.string().min(1)).optional(),
    weight: z.number().int().optional(),
    status: z.string().min(1).optional()
});
//# sourceMappingURL=content-item.js.map