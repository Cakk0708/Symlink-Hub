package distributor

import (
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/cakk/symlink-hub/internal/core"
	"github.com/cakk/symlink-hub/internal/manifest"
)

// Distributor handles file distribution
type Distributor struct {
	dryRun bool
}

// NewDistributor creates a new distributor
func NewDistributor(dryRun bool) *Distributor {
	return &Distributor{dryRun: dryRun}
}

// ExecutePlan executes a build plan
func (d *Distributor) ExecutePlan(plan *core.BuildPlan) error {
	for _, entry := range plan.Entries {
		if entry.Action == core.BuildActionSkip || entry.Action == core.BuildActionConflict {
			continue
		}

		if err := d.executeEntry(entry); err != nil {
			return fmt.Errorf("failed to execute %s on %s: %w", entry.Action, entry.OutputPath, err)
		}
	}
	return nil
}

// executeEntry executes a single build plan entry
func (d *Distributor) executeEntry(entry core.BuildPlanEntry) error {
	switch entry.Action {
	case core.BuildActionCreate, core.BuildActionReplace:
		return d.createOrUpdate(entry)
	case core.BuildActionDelete:
		return d.delete(entry)
	default:
		return nil
	}
}

// createOrUpdate creates or updates a file
func (d *Distributor) createOrUpdate(entry core.BuildPlanEntry) error {
	// Ensure target directory exists
	dir := filepath.Dir(entry.OutputPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Remove existing file/symlink if it exists
	if _, err := os.Lstat(entry.OutputPath); err == nil {
		if err := os.Remove(entry.OutputPath); err != nil {
			return fmt.Errorf("failed to remove existing file: %w", err)
		}
	}

	switch entry.Mode {
	case string(core.DistributionModeSymlink):
		return d.createSymlink(entry)
	case string(core.DistributionModeCopy):
		return d.createCopy(entry)
	default:
		return fmt.Errorf("unknown distribution mode: %s", entry.Mode)
	}
}

// createSymlink creates a symbolic link
func (d *Distributor) createSymlink(entry core.BuildPlanEntry) error {
	// Get source path from first source item
	if len(entry.SourceItems) == 0 {
		return fmt.Errorf("no source items specified")
	}

	// For now, assume source is the content item path
	// In a real implementation, we'd look up the source path from the content item
	sourcePath := entry.SourceItems[0]

	if d.dryRun {
		fmt.Printf("Would symlink: %s -> %s\n", entry.OutputPath, sourcePath)
		return nil
	}

	if err := os.Symlink(sourcePath, entry.OutputPath); err != nil {
		return fmt.Errorf("failed to create symlink: %w", err)
	}

	return nil
}

// createCopy copies a file
func (d *Distributor) createCopy(entry core.BuildPlanEntry) error {
	if len(entry.SourceItems) == 0 {
		return fmt.Errorf("no source items specified")
	}

	sourcePath := entry.SourceItems[0]

	if d.dryRun {
		fmt.Printf("Would copy: %s -> %s\n", sourcePath, entry.OutputPath)
		return nil
	}

	src, err := os.Open(sourcePath)
	if err != nil {
		return fmt.Errorf("failed to open source: %w", err)
	}
	defer src.Close()

	dst, err := os.Create(entry.OutputPath)
	if err != nil {
		return fmt.Errorf("failed to create destination: %w", err)
	}
	defer dst.Close()

	if _, err := io.Copy(dst, src); err != nil {
		return fmt.Errorf("failed to copy: %w", err)
	}

	return nil
}

// delete deletes a file
func (d *Distributor) delete(entry core.BuildPlanEntry) error {
	if d.dryRun {
		fmt.Printf("Would delete: %s\n", entry.OutputPath)
		return nil
	}

	if err := os.Remove(entry.OutputPath); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to delete: %w", err)
	}

	return nil
}

// DeleteFile deletes a file by path
func (d *Distributor) DeleteFile(path string) error {
	return d.deletePath(path)
}

// CleanEntry cleans a manifest entry
func (d *Distributor) CleanEntry(entry manifest.Entry) error {
	return d.deletePath(entry.OutputPath)
}

func (d *Distributor) deletePath(path string) error {
	if d.dryRun {
		fmt.Printf("Would delete: %s\n", path)
		return nil
	}

	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to delete: %w", err)
	}

	// Try to remove parent directory if empty
	dir := filepath.Dir(path)
	if entries, err := os.ReadDir(dir); err == nil && len(entries) == 0 {
		os.Remove(dir)
	}

	return nil
}
