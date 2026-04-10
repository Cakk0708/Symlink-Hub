package core

// ContentType represents the type of content
type ContentType string

const (
	ContentTypeAgent   ContentType = "agent"
	ContentTypeSkill   ContentType = "skill"
	ContentTypeRule    ContentType = "rule"
	ContentTypeDoc     ContentType = "doc"
	ContentTypeCommand ContentType = "command"
)

// ContentItem represents a content item from the content store
type ContentItem struct {
	ID           string      `yaml:"id"`
	Title        string      `yaml:"title"`
	Type         ContentType `yaml:"type"`
	Targets      []string    `yaml:"targets,omitempty"`
	Tags         []string    `yaml:"tags,omitempty"`
	Projects     []string    `yaml:"projects,omitempty"`
	Weight       int         `yaml:"weight,omitempty"`
	Status       string      `yaml:"status,omitempty"`
	SourcePath   string      `yaml:"-"` // runtime only
	Checksum     string      `yaml:"-"` // runtime only
	LastModified string      `yaml:"-"` // runtime only
}

// BuildAction represents the action to take for a build plan entry
type BuildAction string

const (
	BuildActionCreate   BuildAction = "create"
	BuildActionReplace BuildAction = "replace"
	BuildActionSkip    BuildAction = "skip"
	BuildActionConflict BuildAction = "conflict"
	BuildActionDelete  BuildAction = "delete"
)

// BuildPlanEntry represents a single entry in the build plan
type BuildPlanEntry struct {
	Action      BuildAction `json:"action"`
	ProjectName string      `json:"projectName"`
	Agent       string      `json:"agent"`
	SourceItems []string    `json:"sourceItems"`
	OutputPath  string      `json:"outputPath"`
	Mode        string      `json:"mode"`
	Reason      string      `json:"reason,omitempty"`
}

// BuildPlan represents the complete build plan
type BuildPlan struct {
	GeneratedAt string          `json:"generatedAt"`
	Entries     []BuildPlanEntry `json:"entries"`
}

// DistributionMode represents the distribution mode
type DistributionMode string

const (
	DistributionModeSymlink DistributionMode = "symlink"
	DistributionModeCopy    DistributionMode = "copy"
)

// ConflictStrategy represents the conflict handling strategy
type ConflictStrategy string

const (
	ConflictStrategySkip    ConflictStrategy = "skip"
	ConflictStrategyReplace ConflictStrategy = "replace"
	ConflictStrategyBackup  ConflictStrategy = "backup"
)
