package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cakk/symlink-hub/internal/config"
	"github.com/cakk/symlink-hub/internal/content"
	"github.com/cakk/symlink-hub/internal/core"
	"github.com/cakk/symlink-hub/internal/distributor"
	"github.com/cakk/symlink-hub/internal/manifest"
	"github.com/cakk/symlink-hub/internal/planner"
	"github.com/cakk/symlink-hub/internal/selector"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	args := os.Args[2:]

	// Load config
	cfg, err := loadConfig()
	if err != nil {
		fmt.Printf("Error loading config: %v\n", err)
		os.Exit(1)
	}

	switch cmd {
	case "sync":
		handleSync(cfg, args)
	case "dry-run":
		handleDryRun(cfg, args)
	case "clean":
		handleClean(cfg, args)
	case "status":
		handleStatus(cfg, args)
	case "doctor":
		handleDoctor(cfg, args)
	default:
		fmt.Printf("Unknown command: %s\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func loadConfig() (*config.Config, error) {
	configPath := "symlink-hub.config.yaml"
	if len(os.Args) > 2 && (os.Args[2] == "--config" || os.Args[2] == "-c") {
		if len(os.Args) < 4 {
			return nil, fmt.Errorf("--config requires a path")
		}
		configPath = os.Args[3]
	}

	absPath, err := filepath.Abs(configPath)
	if err != nil {
		return nil, err
	}

	loader := config.NewLoader(absPath)
	return loader.Load()
}

func printUsage() {
	fmt.Println("Symlink-Hub - Local AI Configuration Content Hub")
	fmt.Println()
	fmt.Println("Usage:")
	fmt.Println("  symlink-hub sync [project] [--agent <name>]")
	fmt.Println("  symlink-hub dry-run [project] [--agent <name>]")
	fmt.Println("  symlink-hub clean [project] [--agent <name>]")
	fmt.Println("  symlink-hub status [project] [--agent <name>]")
	fmt.Println("  symlink-hub doctor")
}

func handleSync(cfg *config.Config, args []string) {
	projectName, agentName := parseArgs(args)

	items := scanAndValidate(cfg)
	projects := getProjects(cfg, projectName)
	agents := getAgents(cfg, agentName)

	sel := selector.NewSelector(cfg)
	planner := planner.NewPlanner(cfg)
	dist := distributor.NewDistributor(false)
	manifestMgr := manifest.NewManager(cfg.StateRoot)

	for _, proj := range projects {
		for _, agent := range agents {
			fmt.Printf("\n=== Syncing %s @ %s ===\n", agent, proj.Name)

			selected := sel.Select(items, selector.Options{
				ProjectName: proj.Name,
				Agent:       agent,
			})

			plan, err := planner.GeneratePlan(selected, proj.Name, agent)
			if err != nil {
				fmt.Printf("Error generating plan: %v\n", err)
				continue
			}

			planner.PrintPlan(plan)

			if len(plan.Entries) > 0 {
				fmt.Printf("Executing distribution...\n")
				if err := dist.ExecutePlan(plan); err != nil {
					fmt.Printf("Error executing plan: %v\n", err)
					continue
				}

				if err := manifestMgr.Write(plan, proj.Name, agent); err != nil {
					fmt.Printf("Warning: failed to write manifest: %v\n", err)
				}

				fmt.Printf("✓ Sync complete\n")
			}
		}
	}
}

func handleDryRun(cfg *config.Config, args []string) {
	projectName, agentName := parseArgs(args)

	items := scanAndValidate(cfg)
	projects := getProjects(cfg, projectName)
	agents := getAgents(cfg, agentName)

	sel := selector.NewSelector(cfg)
	planner := planner.NewPlanner(cfg)

	for _, proj := range projects {
		for _, agent := range agents {
			fmt.Printf("\n=== %s @ %s ===\n", agent, proj.Name)

			selected := sel.Select(items, selector.Options{
				ProjectName: proj.Name,
				Agent:       agent,
			})

			plan, err := planner.GeneratePlan(selected, proj.Name, agent)
			if err != nil {
				fmt.Printf("Error generating plan: %v\n", err)
				continue
			}

			planner.PrintPlan(plan)
		}
	}
}

func handleClean(cfg *config.Config, args []string) {
	projectName, agentName := parseArgs(args)

	projects := getProjects(cfg, projectName)
	agents := getAgents(cfg, agentName)

	manifestMgr := manifest.NewManager(cfg.StateRoot)
	dist := distributor.NewDistributor(false)

	for _, proj := range projects {
		for _, agent := range agents {
			fmt.Printf("\n=== Cleaning %s @ %s ===\n", agent, proj.Name)

			mft, err := manifestMgr.Read(proj.Name, agent)
			if err != nil {
				fmt.Printf("No manifest found for %s @ %s\n", agent, proj.Name)
				continue
			}

			fmt.Printf("Found %d entries in manifest\n", len(mft.Entries))

			deletedCount := 0
			for i := len(mft.Entries) - 1; i >= 0; i-- {
				entry := mft.Entries[i]
				if err := dist.DeleteFile(entry.OutputPath); err != nil {
					fmt.Printf("Warning: failed to delete %s: %v\n", entry.OutputPath, err)
				} else {
					deletedCount++
				}
			}

			manifestMgr.Remove(proj.Name, agent)
			fmt.Printf("✓ Cleaned %d files\n", deletedCount)
		}
	}
}

func handleStatus(cfg *config.Config, args []string) {
	fmt.Println("Status command - under construction")
}

func handleDoctor(cfg *config.Config, args []string) {
	fmt.Println("Running diagnostics...")

	if _, err := os.Stat(cfg.ContentRoot); os.IsNotExist(err) {
		fmt.Printf("✗ Content root does not exist: %s\n", cfg.ContentRoot)
	} else {
		fmt.Printf("✓ Content root exists: %s\n", cfg.ContentRoot)
	}

	if _, err := os.Stat(cfg.StateRoot); os.IsNotExist(err) {
		fmt.Printf("✗ State root does not exist: %s\n", cfg.StateRoot)
	} else {
		fmt.Printf("✓ State root exists: %s\n", cfg.StateRoot)
	}

	scanner := content.NewScanner(cfg.ContentRoot)
	items, err := scanner.Scan()
	if err != nil {
		fmt.Printf("✗ Error scanning content: %v\n", err)
	} else {
		fmt.Printf("✓ Found %d content items\n", len(items))
	}

	if err := content.ValidateContentItems(items); err != nil {
		fmt.Printf("✗ Validation failed: %v\n", err)
	} else {
		fmt.Printf("✓ All content items valid\n")
	}

	for _, proj := range cfg.Projects {
		if _, err := os.Stat(proj.Path); os.IsNotExist(err) {
			fmt.Printf("✗ Project path does not exist: %s (%s)\n", proj.Name, proj.Path)
		} else {
			fmt.Printf("✓ Project path exists: %s\n", proj.Name)
		}
	}

	fmt.Printf("\n✓ Configured agents: %d\n", len(cfg.Agents))
	fmt.Printf("✓ Configured projects: %d\n", len(cfg.Projects))
}

func parseArgs(args []string) (projectName, agentName string) {
	projectName = "all"
	agentName = ""
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--agent":
			if i+1 < len(args) {
				agentName = args[i+1]
				i++
			}
		default:
			if !strings.HasPrefix(args[i], "--") {
				projectName = args[i]
			}
		}
	}
	return
}

func scanAndValidate(cfg *config.Config) []core.ContentItem {
	scanner := content.NewScanner(cfg.ContentRoot)
	items, err := scanner.Scan()
	if err != nil {
		fmt.Printf("Error scanning content: %v\n", err)
		os.Exit(1)
	}

	if err := content.ValidateContentItems(items); err != nil {
		fmt.Printf("Validation error: %v\n", err)
		os.Exit(1)
	}

	return items
}

func getProjects(cfg *config.Config, name string) []config.ProjectConfig {
	if name == "all" {
		return cfg.Projects
	}
	for _, p := range cfg.Projects {
		if p.Name == name {
			return []config.ProjectConfig{p}
		}
	}
	return []config.ProjectConfig{}
}

func getAgents(cfg *config.Config, name string) []string {
	if name == "" {
		agents := make([]string, 0, len(cfg.Agents))
		for a := range cfg.Agents {
			agents = append(agents, a)
		}
		return agents
	}
	if _, ok := cfg.Agents[name]; ok {
		return []string{name}
	}
	return []string{}
}
