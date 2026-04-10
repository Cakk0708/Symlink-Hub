package content

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cakk/symlink-hub/internal/core"
)

// Scanner scans content directory for markdown files
type Scanner struct {
	contentRoot string
}

// NewScanner creates a new content scanner
func NewScanner(contentRoot string) *Scanner {
	return &Scanner{contentRoot: contentRoot}
}

// Scan scans the content directory and returns all content items
func (s *Scanner) Scan() ([]core.ContentItem, error) {
	var items []core.ContentItem

	err := filepath.Walk(s.contentRoot, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if !strings.HasSuffix(strings.ToLower(path), ".md") {
			return nil
		}

		item, err := ParseContentFile(path, s.contentRoot)
		if err != nil {
			// Log warning but continue scanning
			fmt.Fprintf(os.Stderr, "Warning: failed to parse %s: %v\n", path, err)
			return nil
		}

		items = append(items, item)
		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to scan content directory: %w", err)
	}

	return items, nil
}

// GetRelativePath returns the relative path from content root
func (s *Scanner) GetRelativePath(fullPath string) string {
	rel, err := filepath.Rel(s.contentRoot, fullPath)
	if err != nil {
		return fullPath
	}
	return rel
}
