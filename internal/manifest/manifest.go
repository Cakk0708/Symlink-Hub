package manifest

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/cakk/symlink-hub/internal/core"
)

// Entry represents a single entry in the manifest
type Entry struct {
	SourceItemIDs []string `json:"sourceItemIds"`
	SourcePath    string   `json:"sourcePath"`
	OutputPath    string   `json:"outputPath"`
	Action        string   `json:"action"`
	Checksum      string   `json:"checksum"`
}

// Manifest represents the sync manifest for a project/agent
type Manifest struct {
	ProjectName string    `json:"projectName"`
	Agent       string    `json:"agent"`
	GeneratedAt string    `json:"generatedAt"`
	Mode        string    `json:"mode"`
	Entries     []Entry   `json:"entries"`
}

// Manager handles manifest operations
type Manager struct {
	stateRoot string
}

// NewManager creates a new manifest manager
func NewManager(stateRoot string) *Manager {
	return &Manager{stateRoot: stateRoot}
}

// Write writes a manifest for a project/agent
func (m *Manager) Write(plan *core.BuildPlan, projectName, agent string) error {
	// Ensure manifests directory exists
	manifestsDir := filepath.Join(m.stateRoot, "manifests")
	if err := os.MkdirAll(manifestsDir, 0755); err != nil {
		return fmt.Errorf("failed to create manifests directory: %w", err)
	}

	// Create manifest
	manifest := &Manifest{
		ProjectName: projectName,
		Agent:       agent,
		GeneratedAt: time.Now().Format(time.RFC3339),
		Mode:        "",
		Entries:     []Entry{},
	}

	// Convert plan entries to manifest entries
	for _, entry := range plan.Entries {
		if entry.Action == core.BuildActionSkip || entry.Action == core.BuildActionConflict {
			continue
		}

		manifestEntry := Entry{
			SourceItemIDs: entry.SourceItems,
			OutputPath:    entry.OutputPath,
			Action:        string(entry.Action),
		}

		// For now, use the first source item as source path
		if len(entry.SourceItems) > 0 {
			manifestEntry.SourcePath = entry.SourceItems[0]
		}

		manifest.Entries = append(manifest.Entries, manifestEntry)
		manifest.Mode = entry.Mode
	}

	// Write manifest to file
	manifestPath := filepath.Join(manifestsDir, fmt.Sprintf("%s.%s.json", projectName, agent))
	data, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal manifest: %w", err)
	}

	if err := os.WriteFile(manifestPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write manifest: %w", err)
	}

	return nil
}

// Read reads a manifest for a project/agent
func (m *Manager) Read(projectName, agent string) (*Manifest, error) {
	manifestPath := filepath.Join(m.stateRoot, "manifests", fmt.Sprintf("%s.%s.json", projectName, agent))

	data, err := os.ReadFile(manifestPath)
	if err != nil {
		return nil, err
	}

	var mft Manifest
	if err := json.Unmarshal(data, &mft); err != nil {
		return nil, fmt.Errorf("failed to unmarshal manifest: %w", err)
	}

	return &mft, nil
}

// Remove removes a manifest file
func (m *Manager) Remove(projectName, agent string) error {
	manifestPath := filepath.Join(m.stateRoot, "manifests", fmt.Sprintf("%s.%s.json", projectName, agent))
	return os.Remove(manifestPath)
}
