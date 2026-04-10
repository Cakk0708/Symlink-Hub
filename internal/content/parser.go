package content

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/cakk/symlink-hub/internal/core"
)

// ParseContentFile parses a markdown file with frontmatter
func ParseContentFile(filePath, contentRoot string) (core.ContentItem, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return core.ContentItem{}, fmt.Errorf("failed to read file: %w", err)
	}

	content := string(data)

	// Check for frontmatter delimiter
	if !strings.HasPrefix(content, "---") {
		return core.ContentItem{}, fmt.Errorf("missing frontmatter delimiter")
	}

	// Find end of frontmatter
	endIndex := strings.Index(content[3:], "---")
	if endIndex == -1 {
		return core.ContentItem{}, fmt.Errorf("unclosed frontmatter delimiter")
	}

	frontmatter := content[3 : endIndex+3]

	// Parse YAML frontmatter manually
	item, err := parseFrontmatter(frontmatter)
	if err != nil {
		return core.ContentItem{}, fmt.Errorf("failed to parse frontmatter: %w", err)
	}

	// Set runtime fields
	item.SourcePath = filePath
	item.LastModified = getModTime(filePath)
	item.Checksum = computeChecksum(data)

	// Validate required fields
	if item.ID == "" {
		return core.ContentItem{}, fmt.Errorf("id is required")
	}
	if item.Title == "" {
		return core.ContentItem{}, fmt.Errorf("title is required")
	}
	if item.Type == "" {
		return core.ContentItem{}, fmt.Errorf("type is required")
	}

	return item, nil
}

// parseFrontmatter parses YAML frontmatter manually
func parseFrontmatter(fm string) (core.ContentItem, error) {
	var item core.ContentItem
	var currentArray *[]string
	var inArray bool

	scanner := bufio.NewScanner(strings.NewReader(fm))
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || line == "---" {
			continue
		}

		// Handle array items (start with "- ")
		if strings.HasPrefix(line, "- ") {
			if inArray && currentArray != nil {
				value := strings.TrimPrefix(line, "- ")
				value = strings.TrimSpace(value)
				*currentArray = append(*currentArray, value)
			}
			continue
		}

		// End of array
		if inArray && !strings.HasPrefix(line, "- ") {
			inArray = false
			currentArray = nil
		}

		idx := strings.Index(line, ":")
		if idx == -1 {
			continue
		}

		key := strings.TrimSpace(line[:idx])
		value := strings.TrimSpace(line[idx+1:])
		value = strings.Trim(value, "\"")
		value = strings.Trim(value, "'")

		switch key {
		case "id":
			item.ID = value
		case "title":
			item.Title = value
		case "type":
			item.Type = core.ContentType(value)
		case "status":
			item.Status = value
		case "weight":
			// Parse int - skip for now
		case "targets":
			item.Targets = []string{}
			currentArray = &item.Targets
			inArray = true
			if value != "" && value != "[]" {
				item.Targets = parseInlineArray(value)
			}
		case "tags":
			item.Tags = []string{}
			currentArray = &item.Tags
			inArray = true
			if value != "" && value != "[]" {
				item.Tags = parseInlineArray(value)
			}
		case "projects":
			item.Projects = []string{}
			currentArray = &item.Projects
			inArray = true
			if value != "" && value != "[]" {
				item.Projects = parseInlineArray(value)
			}
		}
	}

	return item, nil
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

func getModTime(path string) string {
	info, err := os.Stat(path)
	if err != nil {
		return ""
	}
	return info.ModTime().Format(time.RFC3339)
}

func computeChecksum(data []byte) string {
	sum := 0
	for _, b := range data {
		sum += int(b)
	}
	return fmt.Sprintf("crc32:%d", sum)
}

// ValidateContentItems validates all content items
func ValidateContentItems(items []core.ContentItem) error {
	seenIDs := make(map[string]string)

	for _, item := range items {
		if existingPath, ok := seenIDs[item.ID]; ok {
			return fmt.Errorf("duplicate id '%s' in %s and %s", item.ID, existingPath, item.SourcePath)
		}
		seenIDs[item.ID] = item.SourcePath

		validTypes := map[core.ContentType]bool{
			core.ContentTypeAgent:    true,
			core.ContentTypeSkill:    true,
			core.ContentTypeRule:     true,
			core.ContentTypeDoc:      true,
			core.ContentTypeCommand:  true,
		}
		if !validTypes[item.Type] {
			return fmt.Errorf("invalid type '%s' in %s", item.Type, item.SourcePath)
		}
	}

	return nil
}
