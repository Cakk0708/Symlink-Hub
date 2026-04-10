package config

// AgentConfig defines the configuration for an AI agent
type AgentConfig struct {
	AgentFileName string            `yaml:"agentFileName"`
	Roots         map[string]string `yaml:"roots"`
}

// ProjectConfig defines the configuration for a project
type ProjectConfig struct {
	Name        string   `yaml:"name"`
	Path        string   `yaml:"path"`
	Agents      []string `yaml:"agents"`
	IncludeTags []string `yaml:"includeTags,omitempty"`
	ExcludeTags []string `yaml:"excludeTags,omitempty"`
	Features    []string `yaml:"features,omitempty"`
	Mode        string   `yaml:"mode,omitempty"`
	Conflict    string   `yaml:"conflict,omitempty"`
}

// Config represents the root configuration
type Config struct {
	ContentRoot string                    `yaml:"contentRoot"`
	StateRoot   string                    `yaml:"stateRoot"`
	DefaultMode string                    `yaml:"defaultMode"`
	Agents      map[string]AgentConfig    `yaml:"agents"`
	Projects    []ProjectConfig           `yaml:"projects"`
}
