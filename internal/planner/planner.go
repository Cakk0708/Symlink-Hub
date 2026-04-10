package planner

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/cakk/symlink-hub/internal/config"
	"github.com/cakk/symlink-hub/internal/core"
	"github.com/cakk/symlink-hub/internal/mapper"
)

// Planner generates build plans
type Planner struct {
	cfg    *config.Config
	mapper *mapper.Mapper
}

// NewPlanner creates a new build planner
func NewPlanner(cfg *config.Config) *Planner {
	return &Planner{
		cfg:    cfg,
		mapper: mapper.NewMapper(cfg),
	}
}

// GeneratePlan generates a build plan for the given items
func (p *Planner) GeneratePlan(items []core.ContentItem, projectName, agentName string) (*core.BuildPlan, error) {
	projConfig, err := p.mapper.GetProject(projectName)
	if err != nil {
		return nil, err
	}

	mode := projConfig.Mode
	if mode == "" {
		mode = p.cfg.DefaultMode
	}

	plan := &core.BuildPlan{
		GeneratedAt: time.Now().Format(time.RFC3339),
		Entries:     []core.BuildPlanEntry{},
	}

	// Track agent items to detect conflicts
	agentItems := make(map[string][]core.ContentItem)

	for _, item := range items {
		if item.Type == core.ContentTypeAgent {
			agentItems[agentName] = append(agentItems[agentName], item)
		}
	}

	// Check for agent conflicts
	if len(agentItems[agentName]) > 1 {
		// Multiple agent items - conflict
		for _, item := range agentItems[agentName] {
			outputPath, _ := p.mapper.MapOutputPath(item, projectName, agentName)
			plan.Entries = append(plan.Entries, core.BuildPlanEntry{
				Action:      core.BuildActionConflict,
				ProjectName: projectName,
				Agent:       agentName,
				SourceItems: []string{item.ID},
				OutputPath:  outputPath,
				Mode:        mode,
				Reason:      "multiple agent items defined for this project",
			})
		}
		return plan, nil
	}

	// Process all items
	for _, item := range items {
		outputPath, err := p.mapper.MapOutputPath(item, projectName, agentName)
		if err != nil {
			return nil, fmt.Errorf("failed to map output path for %s: %w", item.ID, err)
		}

		action := p.determineAction(outputPath, mode, *projConfig)
		if action == core.BuildActionSkip {
			continue
		}

		plan.Entries = append(plan.Entries, core.BuildPlanEntry{
			Action:      action,
			ProjectName: projectName,
			Agent:       agentName,
			SourceItems: []string{item.SourcePath},
			OutputPath:  outputPath,
			Mode:        mode,
		})
	}

	return plan, nil
}

// determineAction determines what action to take for a file
func (p *Planner) determineAction(outputPath, mode string, proj config.ProjectConfig) core.BuildAction {
	// Check if file exists
	if _, err := os.Stat(outputPath); os.IsNotExist(err) {
		return core.BuildActionCreate
	}

	// File exists - check if it's a symlink
	if info, err := os.Lstat(outputPath); err == nil {
		if info.Mode()&os.ModeSymlink != 0 {
			// Existing symlink - replace
			return core.BuildActionReplace
		}
	}

	// Regular file exists - check conflict strategy
	switch proj.Conflict {
	case "replace":
		return core.BuildActionReplace
	case "skip":
		return core.BuildActionSkip
	default:
		return core.BuildActionSkip
	}
}

// PrintPlan prints the build plan in a readable format
func (p *Planner) PrintPlan(plan *core.BuildPlan) {
	fmt.Printf("\nBuild Plan (generated at %s)\n", plan.GeneratedAt)
	fmt.Println(strings.Repeat("-", 60))

	// Group by action
	actions := map[core.BuildAction][]core.BuildPlanEntry{
		core.BuildActionCreate:   {},
		core.BuildActionReplace: {},
		core.BuildActionSkip:    {},
		core.BuildActionConflict: {},
	}

	for _, entry := range plan.Entries {
		actions[entry.Action] = append(actions[entry.Action], entry)
	}

	// Print creates
	if len(actions[core.BuildActionCreate]) > 0 {
		fmt.Printf("\nCREATE (%d):\n", len(actions[core.BuildActionCreate]))
		for _, e := range actions[core.BuildActionCreate] {
			fmt.Printf("  + %s\n", e.OutputPath)
		}
	}

	// Print replaces
	if len(actions[core.BuildActionReplace]) > 0 {
		fmt.Printf("\nREPLACE (%d):\n", len(actions[core.BuildActionReplace]))
		for _, e := range actions[core.BuildActionReplace] {
			fmt.Printf("  ~ %s\n", e.OutputPath)
		}
	}

	// Print conflicts
	if len(actions[core.BuildActionConflict]) > 0 {
		fmt.Printf("\nCONFLICTS (%d):\n", len(actions[core.BuildActionConflict]))
		for _, e := range actions[core.BuildActionConflict] {
			fmt.Printf("  ! %s - %s\n", e.OutputPath, e.Reason)
		}
	}

	fmt.Printf("\nTotal: %d actions\n", len(plan.Entries))
	fmt.Println()
}
