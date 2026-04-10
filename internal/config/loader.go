package config

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Loader handles configuration loading
type Loader struct {
	configPath string
}

// NewLoader creates a new configuration loader
func NewLoader(configPath string) *Loader {
	return &Loader{configPath: configPath}
}

// Load loads the configuration from file
func (l *Loader) Load() (*Config, error) {
	file, err := os.Open(l.configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}
	defer file.Close()

	cfg := &Config{
		ContentRoot: "./fixtures/content",
		StateRoot:   "./.symlink-hub",
		DefaultMode: "symlink",
		Agents:      make(map[string]AgentConfig),
	}

	scanner := bufio.NewScanner(file)
	var currentAgent string
	var currentProject *ProjectConfig
	var currentArrayName string
	var lastIndent int

	for scanner.Scan() {
		line := scanner.Text()
		trimmed := strings.TrimSpace(line)

		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			continue
		}

		indent := len(line) - len(strings.TrimLeft(line, " \t"))

		// Section headers (only at indent 0)
		if indent == 0 && (trimmed == "agents:" || trimmed == "projects:") {
			currentAgent = ""
			currentProject = nil
			lastIndent = indent
			continue
		}

		// New agent (e.g., "  codex:")
		if indent == 2 && strings.HasSuffix(trimmed, ":") && !strings.Contains(trimmed, "name:") {
			agentName := strings.TrimSuffix(trimmed, ":")
			cfg.Agents[agentName] = AgentConfig{
				Roots: make(map[string]string),
			}
			currentAgent = agentName
			currentProject = nil
			currentArrayName = ""
			continue
		}

		// New project (e.g., "  - name: backend")
		if indent == 2 && strings.HasPrefix(trimmed, "-") {
			cfg.Projects = append(cfg.Projects, ProjectConfig{
				Agents:   []string{},
				Mode:     cfg.DefaultMode,
				Conflict: "skip",
			})
			currentProject = &cfg.Projects[len(cfg.Projects)-1]
			currentAgent = ""
			currentArrayName = ""

			// Parse inline name if present
			if idx := strings.Index(trimmed, "name:"); idx != -1 {
				name := strings.TrimSpace(trimmed[idx+5:])
				name = strings.Trim(name, ":")
				name = strings.TrimSpace(name)
				currentProject.Name = name
			}
			continue
		}

		// Array item (e.g., "    - codex")
		if strings.HasPrefix(trimmed, "- ") {
			value := strings.TrimSpace(trimmed[2:])
			if currentProject != nil && currentArrayName != "" {
				switch currentArrayName {
				case "agents":
					currentProject.Agents = append(currentProject.Agents, value)
				case "includeTags":
					currentProject.IncludeTags = append(currentProject.IncludeTags, value)
				case "excludeTags":
					currentProject.ExcludeTags = append(currentProject.ExcludeTags, value)
				case "features":
					currentProject.Features = append(currentProject.Features, value)
				}
			}
			lastIndent = indent
			continue
		}

		// End of array (indent decreased)
		if indent < lastIndent && indent <= 4 {
			currentArrayName = ""
		}

		// Key-value pair
		if idx := strings.Index(trimmed, ":"); idx != -1 {
			key := strings.TrimSpace(trimmed[:idx])
			value := strings.TrimSpace(trimmed[idx+1:])
			value = strings.Trim(value, "\"")

			// Root level
			if indent == 0 {
				switch key {
				case "contentRoot":
					cfg.ContentRoot = value
				case "stateRoot":
					cfg.StateRoot = value
				case "defaultMode":
					cfg.DefaultMode = value
				}
				continue
			}

			// Agent level
			if currentAgent != "" && indent >= 4 {
				agent := cfg.Agents[currentAgent]
				switch key {
				case "agentFileName":
					agent.AgentFileName = value
					cfg.Agents[currentAgent] = agent
				case "roots":
					// Next lines will be roots
				default:
					// Root entry (e.g., "skill: .codex/skills")
					if indent == 6 {
						agent.Roots[key] = value
						cfg.Agents[currentAgent] = agent
					}
				}
				continue
			}

			// Project level
			if currentProject != nil && indent >= 4 {
				switch key {
				case "name":
					currentProject.Name = value
				case "path":
					currentProject.Path = value
				case "agents":
					currentArrayName = "agents"
					if value != "" {
						currentProject.Agents = parseInlineArray(value)
					}
				case "includeTags":
					currentArrayName = "includeTags"
					if value != "" {
						currentProject.IncludeTags = parseInlineArray(value)
					}
				case "excludeTags":
					currentArrayName = "excludeTags"
					if value != "" {
						currentProject.ExcludeTags = parseInlineArray(value)
					}
				case "features":
					currentArrayName = "features"
					if value != "" {
						currentProject.Features = parseInlineArray(value)
					}
				case "mode":
					currentProject.Mode = value
				case "conflict":
					currentProject.Conflict = value
				}
				continue
			}
		}

		lastIndent = indent
	}

	// Convert to absolute paths
	baseDir := filepath.Dir(l.configPath)
	if !filepath.IsAbs(cfg.ContentRoot) {
		cfg.ContentRoot = filepath.Join(baseDir, cfg.ContentRoot)
	}
	if !filepath.IsAbs(cfg.StateRoot) {
		cfg.StateRoot = filepath.Join(baseDir, cfg.StateRoot)
	}

	for i := range cfg.Projects {
		if !filepath.IsAbs(cfg.Projects[i].Path) {
			cfg.Projects[i].Path = filepath.Join(baseDir, cfg.Projects[i].Path)
		}
	}

	return cfg, nil
}

func parseInlineArray(s string) []string {
	s = strings.Trim(s, "[]")
	if s == "" {
		return []string{}
	}
	parts := strings.Split(s, ",")
	result := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		p = strings.Trim(p, "\"")
		p = strings.Trim(p, "'")
		if p != "" {
			result = append(result, p)
		}
	}
	return result
}
