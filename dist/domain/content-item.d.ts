import { z } from "zod";
export declare const contentTypeSchema: z.ZodEnum<{
    agent: "agent";
    skill: "skill";
    rule: "rule";
    doc: "doc";
    command: "command";
}>;
export declare const contentFrontmatterSchema: z.ZodObject<{
    id: z.ZodString;
    title: z.ZodString;
    type: z.ZodEnum<{
        agent: "agent";
        skill: "skill";
        rule: "rule";
        doc: "doc";
        command: "command";
    }>;
    targets: z.ZodOptional<z.ZodArray<z.ZodString>>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString>>;
    projects: z.ZodOptional<z.ZodArray<z.ZodString>>;
    weight: z.ZodOptional<z.ZodNumber>;
    status: z.ZodOptional<z.ZodString>;
}, z.core.$strip>;
export type ContentType = z.infer<typeof contentTypeSchema>;
export type ContentFrontmatter = z.infer<typeof contentFrontmatterSchema>;
export interface ContentItem extends ContentFrontmatter {
    body: string;
    sourcePath: string;
    relativePath: string;
    checksum: string;
}
