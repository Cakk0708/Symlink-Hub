import type { ContentItem } from "../../domain/content-item.js";

export function validateUniqueContentIds(items: ContentItem[]): void {
  const seen = new Map<string, string>();

  for (const item of items) {
    const existing = seen.get(item.id);
    if (existing) {
      throw new Error(
        `Duplicate content id "${item.id}" found in "${existing}" and "${item.sourcePath}".`
      );
    }

    seen.set(item.id, item.sourcePath);
  }
}
