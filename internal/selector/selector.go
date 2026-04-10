package selector

import (
	"github.com/cakk/symlink-hub/internal/config"
	"github.com/cakk/symlink-hub/internal/core"
)

// Selector handles content selection for projects
type Selector struct {
	cfg *config.Config
}

// NewSelector creates a new content selector
func NewSelector(cfg *config.Config) *Selector {
	return &Selector{cfg: cfg}
}

// Options defines options for content selection
type Options struct {
	ProjectName string
	Agent       string
}

// Select selects content items for a project and agent
func (s *Selector) Select(items []core.ContentItem, opts Options) []core.ContentItem {
	var selected []core.ContentItem

	// Find project config
	var projConfig *config.ProjectConfig
	for i := range s.cfg.Projects {
		if s.cfg.Projects[i].Name == opts.ProjectName {
			projConfig = &s.cfg.Projects[i]
			break
		}
	}
	if projConfig == nil {
		return selected
	}

	// Check if agent is supported by project
	agentSupported := false
	for _, a := range projConfig.Agents {
		if a == opts.Agent {
			agentSupported = true
			break
		}
	}
	if !agentSupported {
		return selected
	}

	// Filter items
	for _, item := range items {
		if s.shouldInclude(item, *projConfig, opts.Agent) {
			selected = append(selected, item)
		}
	}

	return selected
}

// shouldInclude determines if an item should be included
func (s *Selector) shouldInclude(item core.ContentItem, proj config.ProjectConfig, agentName string) bool {
	// Check status
	if item.Status != "" && item.Status != "active" {
		return false
	}

	// Check type support
	if !s.isTypeSupported(item.Type) {
		return false
	}

	// Check targets - if specified, must include this agent
	if len(item.Targets) > 0 {
		found := false
		for _, target := range item.Targets {
			if target == agentName {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}

	// Check projects - if specified, must include this project
	if len(item.Projects) > 0 {
		found := false
		for _, projName := range item.Projects {
			if projName == proj.Name {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}

	// Check include tags
	if len(proj.IncludeTags) > 0 {
		hasMatch := false
		for _, tag := range item.Tags {
			for _, includeTag := range proj.IncludeTags {
				if tag == includeTag {
					hasMatch = true
					break
				}
			}
			if hasMatch {
				break
			}
		}
		if !hasMatch {
			return false
		}
	}

	// Check exclude tags
	for _, tag := range item.Tags {
		for _, excludeTag := range proj.ExcludeTags {
			if tag == excludeTag {
				return false
			}
		}
	}

	return true
}

// isTypeSupported checks if a type is supported
func (s *Selector) isTypeSupported(typ core.ContentType) bool {
	switch typ {
	case core.ContentTypeAgent, core.ContentTypeSkill,
	     core.ContentTypeRule, core.ContentTypeDoc, core.ContentTypeCommand:
		return true
	default:
		return false
	}
}
