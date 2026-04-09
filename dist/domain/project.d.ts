import { z } from "zod";
export declare const agentConfigSchema: z.ZodObject<{
    agentFileName: z.ZodString;
    roots: z.ZodObject<{
        skill: z.ZodString;
        rule: z.ZodString;
        doc: z.ZodString;
        command: z.ZodString;
    }, z.core.$strip>;
}, z.core.$strip>;
export declare const projectConfigSchema: z.ZodObject<{
    name: z.ZodString;
    path: z.ZodString;
    agents: z.ZodArray<z.ZodString>;
    includeTags: z.ZodDefault<z.ZodArray<z.ZodString>>;
    excludeTags: z.ZodDefault<z.ZodArray<z.ZodString>>;
    features: z.ZodDefault<z.ZodArray<z.ZodString>>;
    mode: z.ZodOptional<z.ZodEnum<{
        symlink: "symlink";
        copy: "copy";
    }>>;
    conflict: z.ZodOptional<z.ZodEnum<{
        replace: "replace";
        skip: "skip";
        backup: "backup";
    }>>;
}, z.core.$strip>;
export declare const appConfigSchema: z.ZodObject<{
    contentRoot: z.ZodString;
    stateRoot: z.ZodString;
    defaultMode: z.ZodEnum<{
        symlink: "symlink";
        copy: "copy";
    }>;
    agents: z.ZodRecord<z.ZodString, z.ZodObject<{
        agentFileName: z.ZodString;
        roots: z.ZodObject<{
            skill: z.ZodString;
            rule: z.ZodString;
            doc: z.ZodString;
            command: z.ZodString;
        }, z.core.$strip>;
    }, z.core.$strip>>;
    projects: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        path: z.ZodString;
        agents: z.ZodArray<z.ZodString>;
        includeTags: z.ZodDefault<z.ZodArray<z.ZodString>>;
        excludeTags: z.ZodDefault<z.ZodArray<z.ZodString>>;
        features: z.ZodDefault<z.ZodArray<z.ZodString>>;
        mode: z.ZodOptional<z.ZodEnum<{
            symlink: "symlink";
            copy: "copy";
        }>>;
        conflict: z.ZodOptional<z.ZodEnum<{
            replace: "replace";
            skip: "skip";
            backup: "backup";
        }>>;
    }, z.core.$strip>>;
}, z.core.$strip>;
export declare const supportedMappedTypes: ("skill" | "rule" | "doc" | "command")[];
export type AgentConfig = z.infer<typeof agentConfigSchema>;
export type ProjectConfig = z.infer<typeof projectConfigSchema>;
export type AppConfig = z.infer<typeof appConfigSchema>;
