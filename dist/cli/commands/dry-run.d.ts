export interface DryRunCommandOptions {
    agent?: string;
}
export declare function runDryRunCommand(projectName: string | undefined, options: DryRunCommandOptions): Promise<void>;
