package mapper

import (
	"fmt"
	"path/filepath"

	"github.com/cakk/symlink-hub/internal/config"
	"github.com/cakk/symlink-hub/internal/core"
)

// Mapper maps content items to output paths
type Mapper struct {
	cfg *config.Config
}

// NewMapper creates a new path mapper
func NewMapper(cfg *config.Config) *Mapper {
	return &Mapper{cfg: cfg}
}

// MapOutputPath maps a content item to its output path
func (m *Mapper) MapOutputPath(item core.ContentItem, projectName, agentName string) (string, error) {
	proj, err := m.GetProject(projectName)
	if err != nil {
		return "", err
	}

	agentCfg, ok := m.cfg.Agents[agentName]
	if !ok {
		return "", fmt.Errorf("unknown agent: %s", agentName)
	}

	switch item.Type {
	case core.ContentTypeAgent:
		return filepath.Join(proj.Path, agentCfg.AgentFileName), nil

	case core.ContentTypeSkill:
		root, ok := agentCfg.Roots["skill"]
		if !ok {
			return "", fmt.Errorf("agent %s does not support skill type", agentName)
		}
		return filepath.Join(proj.Path, root, item.ID+".md"), nil

	case core.ContentTypeRule:
		root, ok := agentCfg.Roots["rule"]
		if !ok {
			return "", fmt.Errorf("agent %s does not support rule type", agentName)
		}
		return filepath.Join(proj.Path, root, item.ID+".md"), nil

	case core.ContentTypeDoc:
		root, ok := agentCfg.Roots["doc"]
		if !ok {
			return "", fmt.Errorf("agent %s does not support doc type", agentName)
		}
		return filepath.Join(proj.Path, root, item.ID+".md"), nil

	case core.ContentTypeCommand:
		root, ok := agentCfg.Roots["command"]
		if !ok {
			return "", fmt.Errorf("agent %s does not support command type", agentName)
		}
		return filepath.Join(proj.Path, root, item.ID+".md"), nil

	default:
		return "", fmt.Errorf("unknown content type: %s", item.Type)
	}
}

// GetProject returns a project configuration by name
func (m *Mapper) GetProject(name string) (*config.ProjectConfig, error) {
	for i := range m.cfg.Projects {
		if m.cfg.Projects[i].Name == name {
			return &m.cfg.Projects[i], nil
		}
	}
	return nil, fmt.Errorf("project not found: %s", name)
}
